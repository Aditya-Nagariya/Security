use ratatui::{
    prelude::*,
    symbols::Marker,
    widgets::{canvas::*, *},
};
use crate::core::system::SystemDetector;
use sysinfo::System;

pub struct DashboardState {
    pub cpu_history: Vec<f64>,
    pub window_size: u16,
}

impl DashboardState {
    pub fn new() -> Self {
        Self {
            cpu_history: vec![0.0; 120],
            window_size: 120,
        }
    }

    pub fn on_tick(&mut self, system: &mut System) {
        let usage = system.global_cpu_usage();
        self.cpu_history.push(usage as f64);
        if self.cpu_history.len() > self.window_size as usize {
            self.cpu_history.remove(0);
        }
    }
}

pub fn draw_dashboard(f: &mut Frame, area: Rect, state: &DashboardState) {
    // Visual Constants
    const COL_GLASS_BASE: Color = Color::Rgb(22, 32, 52);
    const COL_NEON_CYAN: Color = Color::Rgb(0, 255, 255);
    const COL_NEON_AMBER: Color = Color::Rgb(255, 191, 0);
    const COL_NEON_CRIMSON: Color = Color::Rgb(220, 20, 60);
    const COL_CHART_COOL_START: Color = Color::Rgb(52, 152, 219);
    const COL_CHART_COOL_END: Color = Color::Rgb(155, 89, 182);
    const COL_CHART_WARM_START: Color = Color::Rgb(230, 126, 34);
    const COL_CHART_WARM_END: Color = Color::Rgb(231, 76, 60);

    let chart_block = Block::default()
        .borders(Borders::ALL)
        .border_style(Style::default().fg(COL_GLASS_BASE))
        .title(" LIVE TELEMETRY ")
        .title_style(Style::default().fg(COL_NEON_CYAN));

    let canvas = Canvas::default()
        .block(chart_block)
        .x_bounds([0.0, state.window_size as f64])
        .y_bounds([0.0, 100.0])
        .marker(Marker::Braille)
        .paint(|ctx| {
            // Grid lines
            for i in 1..5 {
                let y = i as f64 * 20.0;
                ctx.draw(&ratatui::widgets::canvas::Line {
                    x1: 0.0,
                    y1: y,
                    x2: state.window_size as f64,
                    y2: y,
                    color: COL_GLASS_BASE,
                });
            }

            // Data Points
            for (i, &usage) in state.cpu_history.iter().enumerate() {
                let x = i as f64;
                let y = usage;
                
                let (start, end) = if y < 50.0 {
                    (COL_CHART_COOL_START, COL_CHART_COOL_END)
                } else {
                    (COL_CHART_WARM_START, COL_CHART_WARM_END)
                };
                
                let color = interpolate_color(start, end, y / 100.0);
                ctx.print(x, y, Span::styled("•", Style::default().fg(color)));
            }
        });
    
    f.render_widget(canvas, area);
}

fn interpolate_color(start: Color, end: Color, fraction: f64) -> Color {
    let fraction = fraction.clamp(0.0, 1.0);
    if let (Color::Rgb(r1, g1, b1), Color::Rgb(r2, g2, b2)) = (start, end) {
        let r = (r1 as f64 + (r2 as f64 - r1 as f64) * fraction) as u8;
        let g = (g1 as f64 + (g2 as f64 - g1 as f64) * fraction) as u8;
        let b = (b1 as f64 + (b2 as f64 - b1 as f64) * fraction) as u8;
        Color::Rgb(r, g, b)
    } else {
        start 
    }
}
