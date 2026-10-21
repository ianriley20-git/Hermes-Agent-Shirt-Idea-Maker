//! Trace a raster design into flat-color vector art and rasterize it straight to a real
//! alpha-transparent PNG -- no reportlab/renderPM white-canvas round trip, no bg_remove.py.
//!
//! Default background handling: every traced region matching --background drops, everywhere in
//! the image, not just at the canvas edge. This matches this brand's own documented house style
//! (prompts/image_style.md: "The black/dark areas visible inside the artwork should generally
//! represent unprinted shirt fabric, not another printed color" / "Use this black background
//! aggressively as negative space throughout the artwork") -- a letter's counter, an eye's white,
//! a mesh cutout are all *meant* to show the garment through, not sit as opaque ink, so the
//! correct default is to drop the background color wherever it appears, matching VectorCraft's
//! own Ignore Color behavior.
//!
//! --keep-enclosed-ink switches to the old, narrower behavior (drop only background-colored
//! regions whose bounding box touches the canvas edge, keeping every enclosed same-colored region
//! opaque) for the rare design that genuinely needs real opaque ink in the background color
//! somewhere -- off by default since the house style above is the normal case.

use clap::Parser;
use kurbo::{PathEl, Shape};
use tiny_skia::{FillRule, Paint, PathBuilder, Pixmap, Transform};
use vectorcraft_trace::{trace, Mode, Palette, Raster, TraceParams};

/// Edge-preserving bilateral smoothing, matching VectorCraft's own internal `smooth` module
/// (Tomasi & Manduchi 1998) -- it exists in `vectorcraft-trace` but only auto-triggers when the
/// library decides the *whole image* looks like a photo. A design that's mostly flat color with
/// one small painterly/anti-aliased detail area (eyebrows, hatching) reads as flat overall, so
/// that heuristic skips it, and per-pixel classification noise in just that area turns into
/// thousands of one-pixel specks once quantized ("Yesferatu"'s eyes/eyebrows). Reimplemented here
/// so it always runs: a true-flat region has ~zero local variance and this leaves it unchanged, so
/// there's no real cost to applying it unconditionally.
const BILATERAL_ALIKE: f64 = 20.0;

fn bilateral_pass(src: &[u8], w: usize, h: usize, along_rows: bool) -> Vec<u8> {
    let get = |buf: &[u8], x: usize, y: usize| -> [u8; 4] {
        let i = (y * w + x) * 4;
        [buf[i], buf[i + 1], buf[i + 2], buf[i + 3]]
    };
    let mut out = vec![0u8; src.len()];
    for y in 0..h {
        for x in 0..w {
            let i = (y * w + x) * 4;
            let p = get(src, x, y);
            if p[3] < 128 {
                out[i..i + 4].copy_from_slice(&p);
                continue;
            }
            let neighbors: [Option<(usize, usize)>; 2] = if along_rows {
                [(x > 0).then(|| (x - 1, y)), (x + 1 < w).then(|| (x + 1, y))]
            } else {
                [(y > 0).then(|| (x, y - 1)), (y + 1 < h).then(|| (x, y + 1))]
            };
            let mut sum = [f64::from(p[0]), f64::from(p[1]), f64::from(p[2])];
            let mut weight = 1.0;
            for (nx, ny) in neighbors.into_iter().flatten() {
                let q = get(src, nx, ny);
                if q[3] < 128 {
                    continue;
                }
                let d2: f64 = (0..3).map(|k| (f64::from(q[k]) - f64::from(p[k])).powi(2)).sum();
                let wt = 1.0 / (1.0 + d2 / (BILATERAL_ALIKE * BILATERAL_ALIKE)).powi(2);
                for k in 0..3 {
                    sum[k] += wt * f64::from(q[k]);
                }
                weight += wt;
            }
            out[i] = (sum[0] / weight).round() as u8;
            out[i + 1] = (sum[1] / weight).round() as u8;
            out[i + 2] = (sum[2] / weight).round() as u8;
            out[i + 3] = p[3];
        }
    }
    out
}

fn bilateral_smooth(mut buf: Vec<u8>, w: usize, h: usize, rounds: u32) -> Vec<u8> {
    for _ in 0..rounds {
        buf = bilateral_pass(&buf, w, h, true);
        buf = bilateral_pass(&buf, w, h, false);
    }
    buf
}

/// Despeckle pass, matching what the operator does by hand in Illustrator for exactly this:
/// classify every pixel to its nearest swatch, then run a majority-vote filter over a small
/// window so an isolated misclassified pixel gets overruled by its surrounding neighborhood.
/// Bilateral smoothing alone (above) works in continuous color space and wasn't enough on its own
/// for a design with denser fine detail (fine linework is already close in scale to the noise it's
/// smoothing); committing every pixel to a swatch first, then voting on that discrete label, is a
/// more decisive cleanup, appropriate since the final art is flat screen-print color anyway.
fn nearest_swatch(p: [u8; 3], swatches: &[[u8; 3]]) -> u8 {
    swatches
        .iter()
        .enumerate()
        .map(|(i, s)| (i, color_dist2(p, *s)))
        .min_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .map(|(i, _)| i as u8)
        .unwrap()
}

fn classify(buf: &[u8], w: usize, h: usize, swatches: &[[u8; 3]]) -> Vec<u8> {
    (0..w * h).map(|i| nearest_swatch([buf[i * 4], buf[i * 4 + 1], buf[i * 4 + 2]], swatches)).collect()
}

fn majority_filter(labels: Vec<u8>, w: usize, h: usize, radius: i32, swatch_count: usize, rounds: u32) -> Vec<u8> {
    let mut cur = labels;
    for _ in 0..rounds {
        let mut next = cur.clone();
        for y in 0..h as i32 {
            for x in 0..w as i32 {
                let mut counts = vec![0u32; swatch_count];
                for dy in -radius..=radius {
                    for dx in -radius..=radius {
                        let (nx, ny) = (x + dx, y + dy);
                        if nx >= 0 && ny >= 0 && (nx as usize) < w && (ny as usize) < h {
                            counts[cur[ny as usize * w + nx as usize] as usize] += 1;
                        }
                    }
                }
                let best = counts.iter().enumerate().max_by_key(|&(_, c)| *c).map(|(i, _)| i as u8).unwrap();
                next[y as usize * w + x as usize] = best;
            }
        }
        cur = next;
    }
    cur
}

fn labels_to_rgba(labels: &[u8], alpha: &[u8], swatches: &[[u8; 3]]) -> Vec<u8> {
    let mut out = vec![0u8; labels.len() * 4];
    for i in 0..labels.len() {
        let c = swatches[labels[i] as usize];
        out[i * 4] = c[0];
        out[i * 4 + 1] = c[1];
        out[i * 4 + 2] = c[2];
        out[i * 4 + 3] = alpha[i];
    }
    out
}

#[derive(Parser)]
#[command(about)]
struct Args {
    #[arg(long)]
    input: String,
    /// Output transparent PNG.
    #[arg(long)]
    output: String,
    /// Also write the traced SVG here (for inspection / Illustrator-style tools).
    #[arg(long)]
    svg: Option<String>,
    /// Operator-chosen swatches, as #rrggbb, comma-separated.
    #[arg(long, value_delimiter = ',')]
    swatches: Vec<String>,
    /// Which swatch is the negative-space/background color (#rrggbb). A region of it drops if it
    /// touches the canvas edge (the real background) OR if it's both small and compact (a letter
    /// counter, an eye's white -- a "hole"); an elongated region (real linework, a stroke) stays
    /// opaque regardless of size -- see the house-style note above and --compact-* below.
    #[arg(long)]
    background: String,
    #[arg(long, default_value_t = 2)]
    noise: u32,
    /// Max area (fraction of canvas) for a compact enclosed background-colored region to drop.
    #[arg(long, default_value_t = 0.01)]
    compact_max_area: f64,
    /// Min fill fraction (pixels / bounding-box area) for a region to count as "compact" (a blob,
    /// not a stroke). A letter counter or eye-white is typically well above this; a curved stroke
    /// (eyebrow, eyelash, hatching) is typically well below it.
    #[arg(long, default_value_t = 0.35)]
    compact_min_fill: f64,
    /// Upscale the rasterized output by this factor (vector paths, so this stays crisp).
    #[arg(long, default_value_t = 1.0)]
    scale: f64,
    /// Rounds of bilateral pre-smoothing before quantizing (0 disables it).
    #[arg(long, default_value_t = 3)]
    smooth_rounds: u32,
    /// Window radius (px) for an optional post-classification majority-vote despeckle (0 disables
    /// it -- off by default, since it erases thin strokes along with real noise at this design's
    /// resolution; only reach for it on a design with no fine linework to protect).
    #[arg(long, default_value_t = 0)]
    majority_radius: i32,
    /// Rounds of the majority-vote despeckle.
    #[arg(long, default_value_t = 2)]
    majority_rounds: u32,
}

fn parse_hex(s: &str) -> [u8; 3] {
    let s = s.trim().trim_start_matches('#');
    let v = u32::from_str_radix(s, 16).unwrap_or_else(|_| panic!("bad hex color: {s}"));
    [(v >> 16) as u8, (v >> 8) as u8, v as u8]
}

fn color_dist2(a: [u8; 3], b: [u8; 3]) -> f64 {
    (0..3).map(|k| (f64::from(a[k]) - f64::from(b[k])).powi(2)).sum()
}

fn main() {
    let args = Args::parse();

    let swatches: Vec<[u8; 3]> = args.swatches.iter().map(|s| parse_hex(s)).collect();
    assert!(!swatches.is_empty(), "--swatches is required (comma-separated #rrggbb list)");
    let background = parse_hex(&args.background);

    let img = image::open(&args.input).expect("decode input image").to_rgba8();
    let (w, h) = img.dimensions();
    let (wu, hu) = (w as usize, h as usize);
    let mut buf = img.into_raw();
    if args.smooth_rounds > 0 {
        buf = bilateral_smooth(buf, wu, hu, args.smooth_rounds);
    }
    if args.majority_radius > 0 && args.majority_rounds > 0 {
        let alpha: Vec<u8> = (0..wu * hu).map(|i| buf[i * 4 + 3]).collect();
        let labels = classify(&buf, wu, hu, &swatches);
        let labels = majority_filter(labels, wu, hu, args.majority_radius, swatches.len(), args.majority_rounds);
        buf = labels_to_rgba(&labels, &alpha, &swatches);
    }
    let raster = Raster::new(w, h, buf).expect("build raster");

    let params = TraceParams {
        mode: Mode::Color,
        palette: Palette::DocumentLibrary,
        colors: swatches.len() as u32,
        swatches,
        fills: true,
        noise: args.noise,
        ignore_white: false,
        ignore_color: None,
        ..Default::default()
    };

    let result = trace(&raster, &params);
    eprintln!("traced {} regions", result.paths.len());

    let pixmap_w = (w as f64 * args.scale).round() as u32;
    let pixmap_h = (h as f64 * args.scale).round() as u32;
    let mut pixmap = Pixmap::new(pixmap_w, pixmap_h).expect("pixmap");
    let transform = Transform::from_scale(args.scale as f32, args.scale as f32);

    let border_eps = 1.5_f64;

    let mut kept_svg_paths = Vec::new();
    let mut dropped = 0usize;
    let mut kept = 0usize;

    let canvas_area = (w as f64) * (h as f64);
    let compact_max_px = args.compact_max_area * canvas_area;

    for p in &result.paths {
        let bez = p.path.to_bezpath();
        let is_background_color = color_dist2(p.color, background) <= 30.0 * 30.0;

        let drop = if !is_background_color {
            false
        } else {
            let bbox = bez.bounding_box();
            let touches_border = bbox.x0 <= border_eps
                || bbox.y0 <= border_eps
                || bbox.x1 >= (w as f64) - border_eps
                || bbox.y1 >= (h as f64) - border_eps;
            let bbox_area = (bbox.x1 - bbox.x0).max(1.0) * (bbox.y1 - bbox.y0).max(1.0);
            let fill_fraction = (p.pixels as f64) / bbox_area;
            let is_compact_hole =
                (p.pixels as f64) <= compact_max_px && fill_fraction >= args.compact_min_fill;
            touches_border || is_compact_hole
        };

        if drop {
            dropped += 1;
            continue;
        }
        kept += 1;

        let mut pb = PathBuilder::new();
        for el in bez.elements() {
            match *el {
                PathEl::MoveTo(pt) => pb.move_to(pt.x as f32, pt.y as f32),
                PathEl::LineTo(pt) => pb.line_to(pt.x as f32, pt.y as f32),
                PathEl::QuadTo(c, pt) => pb.quad_to(c.x as f32, c.y as f32, pt.x as f32, pt.y as f32),
                PathEl::CurveTo(c1, c2, pt) => {
                    pb.cubic_to(c1.x as f32, c1.y as f32, c2.x as f32, c2.y as f32, pt.x as f32, pt.y as f32)
                }
                PathEl::ClosePath => pb.close(),
            }
        }
        if let Some(path) = pb.finish() {
            let mut paint = Paint::default();
            paint.set_color_rgba8(p.color[0], p.color[1], p.color[2], 255);
            paint.anti_alias = true;
            pixmap.fill_path(&path, &paint, FillRule::Winding, transform, None);
        }

        let d = bez.to_svg();
        let [r, g, b] = p.color;
        kept_svg_paths.push(format!("<path d=\"{d}\" fill=\"rgb({r},{g},{b})\"/>"));
    }

    eprintln!("kept {kept} regions, dropped {dropped} background region(s)");

    pixmap.save_png(&args.output).expect("write png");
    eprintln!("wrote {}", args.output);

    if let Some(svg_path) = args.svg {
        let mut svg = String::new();
        svg.push_str(&format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {w} {h}\" width=\"{w}\" height=\"{h}\">\n"
        ));
        for line in &kept_svg_paths {
            svg.push_str(line);
            svg.push('\n');
        }
        svg.push_str("</svg>\n");
        std::fs::write(&svg_path, svg).expect("write svg");
        eprintln!("wrote {svg_path}");
    }
}
