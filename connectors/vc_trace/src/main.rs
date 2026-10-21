//! Trace a raster design into flat-color vector art and rasterize it straight to a real
//! alpha-transparent PNG -- no reportlab/renderPM white-canvas round trip, no bg_remove.py.
//!
//! Background handling: every traced region matching the background color drops, everywhere in
//! the image, not just at the canvas edge -- equivalent to Illustrator's "Select Same Fill Color,
//! then Delete," and to VectorCraft's own Ignore Color. This matches this brand's own documented
//! house style (prompts/image_style.md: "The black/dark areas visible inside the artwork should
//! generally represent unprinted shirt fabric, not another printed color" / "Use this black
//! background aggressively as negative space throughout the artwork") -- a letter's counter, an
//! eye's white, fine linework like eyebrows/hatching are all *meant* to show the garment through,
//! not sit as opaque ink. Confirmed with the operator on "Yesferatu": this is a deliberate choice,
//! not just tolerated -- negative-space linework (letting the garment's own color stand in for an
//! ink line) is a legitimate screen-print technique they want by default, not a defect to protect
//! real ink from. --background is optional: when omitted, the background color is auto-detected
//! as whichever swatch the most border-touching pixels classify to, so the operator doesn't have
//! to pre-identify it by eye.

use clap::Parser;
use kurbo::PathEl;
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
    nearest_swatch_biased(p, swatches, None, 1.0)
}

/// Nearest-swatch classification with an optional distance bias favoring `background_idx` --
/// scales that swatch's distance down before comparing, so an ambiguous blended pixel (e.g. a
/// black/tan anti-aliased edge that happens to sit numerically closer to an unrelated third
/// swatch like navy, a known coincidence of plain Euclidean RGB distance) resolves toward
/// negative space instead of a wrong opaque color. `bias` < 1.0 favors the background; 1.0 is
/// unbiased nearest-neighbor.
fn nearest_swatch_biased(p: [u8; 3], swatches: &[[u8; 3]], background_idx: Option<usize>, bias: f64) -> u8 {
    swatches
        .iter()
        .enumerate()
        .map(|(i, s)| {
            let d = color_dist2(p, *s);
            let d = if Some(i) == background_idx { d * bias } else { d };
            (i, d)
        })
        .min_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .map(|(i, _)| i as u8)
        .unwrap()
}

fn classify_biased(buf: &[u8], w: usize, h: usize, swatches: &[[u8; 3]], background_idx: usize, bias: f64) -> Vec<u8> {
    (0..w * h)
        .map(|i| nearest_swatch_biased([buf[i * 4], buf[i * 4 + 1], buf[i * 4 + 2]], swatches, Some(background_idx), bias))
        .collect()
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
    /// Which swatch is the negative-space/background color (#rrggbb); every region of it drops,
    /// everywhere in the image -- see the house-style note above. Omit to auto-detect it from
    /// whichever swatch the canvas border itself classifies to.
    #[arg(long)]
    background: Option<String>,
    #[arg(long, default_value_t = 2)]
    noise: u32,
    /// Distance bias (0-1) favoring the background swatch when classifying each pixel; < 1.0
    /// shrinks its effective distance so an ambiguous blended edge pixel resolves toward negative
    /// space instead of landing on an unrelated swatch by Euclidean coincidence (see the
    /// nearest_swatch_biased doc comment). 1.0 disables the bias.
    #[arg(long, default_value_t = 0.5)]
    background_bias: f64,
    /// Paths (fidelity) 0-100: how closely the curve fit follows the pixel edge -- 0.78px
    /// tolerance at 0 (loose/smooth, fewer anchor points), 0.33px at the default 50, 0.08px at 100
    /// (tight/precise). Lower suits a sketchy/distressed source; higher suits crisp flat art.
    #[arg(long, default_value_t = 50.0)]
    paths: f64,
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

    let img = image::open(&args.input).expect("decode input image").to_rgba8();
    let (w, h) = img.dimensions();
    let (wu, hu) = (w as usize, h as usize);
    let mut buf = img.into_raw();
    if args.smooth_rounds > 0 {
        buf = bilateral_smooth(buf, wu, hu, args.smooth_rounds);
    }

    let background_idx: usize = match &args.background {
        Some(s) => {
            let target = parse_hex(s);
            swatches
                .iter()
                .position(|s| color_dist2(*s, target) <= 1.0)
                .unwrap_or_else(|| panic!("--background {s} doesn't match any --swatches entry"))
        }
        None => {
            let mut votes = vec![0u64; swatches.len()];
            let mut border_px = Vec::new();
            for x in 0..wu {
                border_px.push((x, 0));
                border_px.push((x, hu - 1));
            }
            for y in 0..hu {
                border_px.push((0, y));
                border_px.push((wu - 1, y));
            }
            for (x, y) in border_px {
                let i = (y * wu + x) * 4;
                let label = nearest_swatch([buf[i], buf[i + 1], buf[i + 2]], &swatches);
                votes[label as usize] += 1;
            }
            votes.iter().enumerate().max_by_key(|&(_, c)| *c).map(|(i, _)| i).unwrap()
        }
    };
    let background = swatches[background_idx];
    eprintln!("background: #{:02x}{:02x}{:02x}", background[0], background[1], background[2]);

    // Always pre-quantize ourselves (rather than leaving final classification to VectorCraft's
    // own internal DocumentLibrary quantizer) so the background-bias above actually takes effect,
    // and so an optional majority-vote despeckle (below) has discrete labels to vote on.
    let labels = classify_biased(&buf, wu, hu, &swatches, background_idx, args.background_bias);
    let labels = if args.majority_radius > 0 && args.majority_rounds > 0 {
        majority_filter(labels, wu, hu, args.majority_radius, swatches.len(), args.majority_rounds)
    } else {
        labels
    };
    let alpha: Vec<u8> = (0..wu * hu).map(|i| buf[i * 4 + 3]).collect();
    buf = labels_to_rgba(&labels, &alpha, &swatches);

    let raster = Raster::new(w, h, buf).expect("build raster");

    let params = TraceParams {
        mode: Mode::Color,
        palette: Palette::DocumentLibrary,
        colors: swatches.len() as u32,
        swatches,
        fills: true,
        noise: args.noise,
        paths: args.paths,
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

    let mut kept_svg_paths = Vec::new();
    let mut dropped = 0usize;
    let mut kept = 0usize;

    for p in &result.paths {
        let bez = p.path.to_bezpath();
        let drop = color_dist2(p.color, background) <= 30.0 * 30.0;

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
