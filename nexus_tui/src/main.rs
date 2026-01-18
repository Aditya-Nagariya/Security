use anyhow::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    prelude::*,
    widgets::*,
};
use std::{
    io::{self, Stdout},
    time::{Duration, Instant},
};
use sysinfo::{CpuRefreshKind, RefreshKind, System};

mod core;
mod ui;

use crate::core::system::SystemDetector;
use crate::ui::dashboard::{DashboardState, draw_dashboard};
use crate::ui::operations::{OperationsState, draw_operations};

// --- VISUAL CONSTANTS ---
const COL_BG_TOP: Color = Color::Rgb(15, 23, 42);
const COL_BG_BOT: Color = Color::Rgb(8, 14, 28);
const COL_NEON_CYAN: Color = Color::Rgb(0, 255, 255);
const COL_GLASS_BASE: Color = Color::Rgb(22, 32, 52);

enum ActiveTab {
    Dashboard,
    Operations,
}

struct App {
    system: System,
    detector: SystemDetector,
    dashboard: DashboardState,
    operations: OperationsState,
    active_tab: ActiveTab,
    frame_count: u64,
}

impl App {
    fn new() -> Self {
        Self {
            system: System::new_with_specifics(
                RefreshKind::nothing().with_cpu(CpuRefreshKind::everything()),
            ),
            detector: SystemDetector::new(),
            dashboard: DashboardState::new(),
            operations: OperationsState::new(),
            active_tab: ActiveTab::Dashboard,
            frame_count: 0,
        }
    }

    fn on_tick(&mut self) {
        self.frame_count += 1;
        if self.frame_count % 10 == 0 {
            self.system.refresh_cpu_all();
            self.dashboard.on_tick(&mut self.system);
        }
    }
}

fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let app = App::new();
    let res = run_app(&mut terminal, app);

    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        println!("{:?}", err);
    }

    Ok(())
}

fn run_app(terminal: &mut Terminal<CrosstermBackend<Stdout>>, mut app: App) -> Result<()> {
    let tick_rate = Duration::from_millis(16);
    let mut last_tick = Instant::now();

    loop {
        terminal.draw(|f| ui(f, &mut app))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or_else(|| Duration::from_secs(0));

        if crossterm::event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char('q') => return Ok(()),
                        KeyCode::Tab => {
                            app.active_tab = match app.active_tab {
                                ActiveTab::Dashboard => ActiveTab::Operations,
                                ActiveTab::Operations => ActiveTab::Dashboard,
                            };
                        }
                        // Route inputs based on active tab
                        code => match app.active_tab {
                            ActiveTab::Operations => match code {
                                KeyCode::Up | KeyCode::Char('k') => app.operations.previous(),
                                KeyCode::Down | KeyCode::Char('j') => app.operations.next(),
                                KeyCode::Enter => app.operations.execute_selected(&app.detector),
                                _ => {}
                            },
                            _ => {}
                        },
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

fn ui(f: &mut Frame, app: &mut App) {
    let area = f.area();
    
    // Background
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

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(1)
        .constraints([
            Constraint::Length(3), 
            Constraint::Min(10), 
            Constraint::Length(1)
        ])
        .split(area);

    // Header (Tabs)
    let titles = vec![" Dashboard (TAB) ", " Operations "];
    let tabs = Tabs::new(titles)
        .block(Block::default().borders(Borders::BOTTOM).border_style(Style::default().fg(COL_GLASS_BASE)))
        .highlight_style(Style::default().fg(COL_NEON_CYAN).add_modifier(Modifier::BOLD))
        .select(match app.active_tab {
            ActiveTab::Dashboard => 0,
            ActiveTab::Operations => 1,
        });
    f.render_widget(tabs, chunks[0]);

    // Content
    match app.active_tab {
        ActiveTab::Dashboard => draw_dashboard(f, chunks[1], &app.dashboard),
        ActiveTab::Operations => draw_operations(f, chunks[1], &app.operations),
    }

    // Status Bar
    let status = Paragraph::new("NEXUS OBSIDIAN v2.0 | [q] Quit | [Tab] Switch | [Enter] Exec")
        .style(Style::default().fg(Color::DarkGray));
    f.render_widget(status, chunks[2]);
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
