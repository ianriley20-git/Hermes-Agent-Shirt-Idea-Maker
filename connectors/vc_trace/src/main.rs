//! Trace a raster design into flat-color vector art and rasterize it straight to a real
//! alpha-transparent PNG -- no reportlab/renderPM white-canvas round trip, no bg_remove.py.
//!
//! Background handling does NOT use VectorCraft's own Ignore Color (which drops every pixel of
//! that color anywhere in the image). Instead: trace normally with the background color left IN
//! the swatch list, then after tracing, drop only the traced regions of that color whose bounding
//! box touches the canvas edge (the actual background), keeping every enclosed same-colored
//! region (real ink -- a design's own black linework, hatching, pupils, etc.) opaque. This is the
//! fix for the failure mode found on "Yesferatu": that design's fine black line art reads, color
//! -wise, identically to the black canvas behind it, so blanket-dropping "black" ate the art along
//! with the background. See connectors/README.md.
//!
//! An optional --max-enclosed-area still drops small enclosed background-colored regions too
//! (mirrors bg_remove.py's --island-max-fraction), for designs that really do use an enclosed
//! background-colored region as intentional negative space (e.g. a mesh cutout) -- off by default
//! since that's indistinguishable from real linework without operator judgment per design.

use clap::Parser;
use kurbo::{PathEl, Shape};
use tiny_skia::{FillRule, Paint, PathBuilder, Pixmap, Transform};
use vectorcraft_trace::{trace, Mode, Palette, Raster, TraceParams};

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
    /// Which swatch is the canvas background (#rrggbb); its border-touching region is dropped.
    #[arg(long)]
    background: String,
    #[arg(long, default_value_t = 2)]
    noise: u32,
    /// Also drop enclosed (non-border-touching) background-colored regions up to this fraction of
    /// total canvas area. 0 keeps all enclosed regions as opaque ink (the safe default).
    #[arg(long, default_value_t = 0.0)]
    max_enclosed_area: f64,
    /// Upscale the rasterized output by this factor (vector paths, so this stays crisp).
    #[arg(long, default_value_t = 1.0)]
    scale: f64,
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

    let img = image::open(&args.input).expect("decode input image").to_rgba8();
    let (w, h) = img.dimensions();
    let raster = Raster::new(w, h, img.into_raw()).expect("build raster");

    let swatches: Vec<[u8; 3]> = args.swatches.iter().map(|s| parse_hex(s)).collect();
    assert!(!swatches.is_empty(), "--swatches is required (comma-separated #rrggbb list)");
    let background = parse_hex(&args.background);

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

    let max_enclosed_px = args.max_enclosed_area * (w as f64) * (h as f64);
    let border_eps = 1.5_f64;

    let mut kept_svg_paths = Vec::new();
    let mut dropped = 0usize;
    let mut kept = 0usize;

    for p in &result.paths {
        let bez = p.path.to_bezpath();
        let bbox = bez.bounding_box();
        let is_background_color = color_dist2(p.color, background) <= 30.0 * 30.0;

        let touches_border = bbox.x0 <= border_eps
            || bbox.y0 <= border_eps
            || bbox.x1 >= (w as f64) - border_eps
            || bbox.y1 >= (h as f64) - border_eps;

        let drop = is_background_color
            && (touches_border || (p.pixels as f64) <= max_enclosed_px && max_enclosed_px > 0.0);

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
