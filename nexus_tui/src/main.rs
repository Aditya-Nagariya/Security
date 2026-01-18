use anyhow::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    prelude::*,
    symbols::Marker,
    widgets::{canvas::*, *},
};
use std::{
    io::{self, Stdout},
    time::{Duration, Instant},
};
use sysinfo::{CpuRefreshKind, RefreshKind, System};

// --- VISUAL CONSTANTS ---
const COL_BG_TOP: Color = Color::Rgb(15, 23, 42);
const COL_BG_BOT: Color = Color::Rgb(8, 14, 28);
const COL_GLASS_BASE: Color = Color::Rgb(22, 32, 52);

const COL_NEON_CYAN: Color = Color::Rgb(0, 255, 255);
const COL_NEON_AMBER: Color = Color::Rgb(255, 191, 0);
const COL_NEON_CRIMSON: Color = Color::Rgb(220, 20, 60);

const COL_CHART_COOL_START: Color = Color::Rgb(52, 152, 219);
const COL_CHART_COOL_END: Color = Color::Rgb(155, 89, 182);
const COL_CHART_WARM_START: Color = Color::Rgb(230, 126, 34);
const COL_CHART_WARM_END: Color = Color::Rgb(231, 76, 60);

struct App {
    system: System,
    cpu_history: Vec<f64>,
    window_size: u16,
    frame_count: u64,
}

impl App {
    fn new() -> Self {
        Self {
            system: System::new_with_specifics(
                RefreshKind::nothing().with_cpu(CpuRefreshKind::everything()),
            ),
            cpu_history: vec![0.0; 120], // 2x resolution horizontal for 60s approx
            window_size: 120,
            frame_count: 0,
        }
    }

    fn on_tick(&mut self) {
        self.frame_count += 1;
        // Refresh CPU less frequently than 60Hz to save resources, e.g., every 10 frames
        if self.frame_count % 10 == 0 {
            self.system.refresh_cpu_all();
            let usage = self.system.global_cpu_usage();
            self.cpu_history.push(usage as f64);
            if self.cpu_history.len() > self.window_size as usize {
                self.cpu_history.remove(0);
            }
        }
    }
}

fn main() -> Result<()> {
    // Setup Terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Run App
    let app = App::new();
    let res = run_app(&mut terminal, app);

    // Restore Terminal
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        println!("{:?}", err);
    }

    Ok(())
}

fn run_app(terminal: &mut Terminal<CrosstermBackend<Stdout>>, mut app: App) -> Result<()> {
    let tick_rate = Duration::from_millis(16); // ~60 FPS
    let mut last_tick = Instant::now();

    loop {
        terminal.draw(|f| ui(f, &mut app))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or_else(|| Duration::from_secs(0));

        if crossterm::event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    if let KeyCode::Char('q') = key.code {
                        return Ok(());
                    }
                }
            }
        }

        if last_tick.elapsed() >= tick_rate {
            app.on_tick();
            last_tick = Instant::now();
        }
    }
}

// --- RENDERING ENGINE ---

fn ui(f: &mut Frame, app: &mut App) {
    let area = f.area();
    
    // 1. Draw Background Gradient
    // We simulate this by drawing a block for every line with interpolated bg color
    for y in area.top()..area.bottom() {
        let progress = (y as f64) / (area.height as f64);
        let col = interpolate_color(COL_BG_TOP, COL_BG_BOT, progress);
        let buf = f.buffer_mut();
        for x in area.left()..area.right() {
            if let Some(cell) = buf.cell_mut(Position::new(x, y)) {
                cell.set_bg(col);
            }
        }
    }

    // 2. Layout
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(1)
        .constraints([
            Constraint::Length(3), // Header
            Constraint::Min(10),   // Main Chart
            Constraint::Length(3), // Footer
        ])
        .split(area);

    // 3. Header
    let header_style = Style::default().fg(COL_NEON_CYAN).bg(Color::Reset);
    let title = Paragraph::new("NEXUS OBSIDIAN // TERMINAL INTERFACE")
        .style(header_style.add_modifier(Modifier::BOLD))
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::BOTTOM).border_style(Style::default().fg(COL_GLASS_BASE)));
    f.render_widget(title, chunks[0]);

    // 4. Hero Component: CPU Braille Chart
    let chart_block = Block::default()
        .borders(Borders::ALL)
        .border_style(Style::default().fg(COL_GLASS_BASE))
        .title(" CPU UTILIZATION ")
        .title_style(Style::default().fg(COL_NEON_CYAN));

    let canvas = Canvas::default()
        .block(chart_block)
        .x_bounds([0.0, app.window_size as f64])
        .y_bounds([0.0, 100.0])
        .marker(Marker::Braille)
        .paint(|ctx| {
            // Grid lines
            for i in 1..5 {
                let y = i as f64 * 20.0;
                ctx.draw(&ratatui::widgets::canvas::Line {
                    x1: 0.0,
                    y1: y,
                    x2: app.window_size as f64,
                    y2: y,
                    color: COL_GLASS_BASE,
                });
            }

            // Data Points
            for (i, &usage) in app.cpu_history.iter().enumerate() {
                let x = i as f64;
                let y = usage;
                
                // Color Logic
                let (start, end) = if y < 50.0 {
                    (COL_CHART_COOL_START, COL_CHART_COOL_END)
                } else {
                    (COL_CHART_WARM_START, COL_CHART_WARM_END)
                };
                
                // Interpolate based on height (intensity)
                let color = interpolate_color(start, end, y / 100.0);

                // Draw point (Braille marker handles the "pixel")
                ctx.print(x, y, Span::styled("•", Style::default().fg(color)));
                
                // Simple fill effect (draw points below)
                // Optimization: Only draw a few points below to simulate fill without killing perf
                if y > 5.0 { ctx.print(x, y - 2.0, Span::styled("·", Style::default().fg(color.darken()))); }
                if y > 10.0 { ctx.print(x, y - 5.0, Span::styled("·", Style::default().fg(color.darken()))); }
            }
        });
    
    f.render_widget(canvas, chunks[1]);

    // 5. Current Value Indicator (Floating)
    if let Some(&last_val) = app.cpu_history.last() {
        let color = if last_val > 80.0 { COL_NEON_CRIMSON } else if last_val > 50.0 { COL_NEON_AMBER } else { COL_NEON_CYAN };
        let text = format!("{:.1}%", last_val);
        let area = chunks[1]; // Position inside chart area
        let t_area = Rect::new(area.right() - 10, area.top() + 1, 8, 3);
        
        let p = Paragraph::new(text)
            .style(Style::default().fg(color).add_modifier(Modifier::BOLD));
        f.render_widget(p, t_area);
    }
}

// --- UTILS ---

fn interpolate_color(start: Color, end: Color, fraction: f64) -> Color {
    let fraction = fraction.clamp(0.0, 1.0);
    if let (Color::Rgb(r1, g1, b1), Color::Rgb(r2, g2, b2)) = (start, end) {
        let r = (r1 as f64 + (r2 as f64 - r1 as f64) * fraction) as u8;
        let g = (g1 as f64 + (g2 as f64 - g1 as f64) * fraction) as u8;
        let b = (b1 as f64 + (b2 as f64 - b1 as f64) * fraction) as u8;
        Color::Rgb(r, g, b)
    } else {
        start // Fallback
    }
}

trait ColorExt {
    fn darken(&self) -> Color;
}

impl ColorExt for Color {
    fn darken(&self) -> Color {
        if let Color::Rgb(r, g, b) = self {
            Color::Rgb(r * 2 / 3, g * 2 / 3, b * 2 / 3)
        } else {
            *self
        }
    }
}