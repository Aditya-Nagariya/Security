use iced::{
    executor, widget::{button, column, container, row, scrollable, text},
    Application, Command, Element, Length, Settings, Subscription, Theme, time
};
use std::time::Duration;

mod core;
mod system;
mod monitor;
mod ui;

use core::traits::SystemInterface;
use core::types::SystemMetrics;
use system::DefaultSystem;
use monitor::TelemetryCollector;
use ui::components::MetricCard;

pub fn main() -> iced::Result {
    AegisApp::run(Settings {
        antialiasing: true,
        ..Settings::default()
    })
}

struct AegisApp {
    system: DefaultSystem,
    collector: TelemetryCollector,
    metrics: SystemMetrics,
    console_log: Vec<String>,
}

#[derive(Debug, Clone)]
enum Message {
    Tick,
    RunScan,
    ScanCompleted(core::types::SecurityScanResult),
}

impl Application for AegisApp {
    type Executor = executor::Default;
    type Message = Message;
    type Theme = Theme;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (
            Self {
                system: DefaultSystem::default(), // Instantiates MockSystem on macOS
                collector: TelemetryCollector::new(),
                metrics: SystemMetrics::default(),
                console_log: vec![
                    "Aegis Security System Initialized...".to_string(),
                    if cfg!(target_os = "linux") { "Mode: ACTIVE (Linux)" } else { "Mode: SIMULATION (Non-Linux)" }.to_string()
                ],
            },
            Command::none(),
        )
    }

    fn title(&self) -> String {
        String::from("Aegis Security Dashboard")
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::Tick => {
                self.metrics = self.collector.collect();
                Command::none()
            }
            Message::RunScan => {
                self.console_log.push("Starting security scan...".to_string());
                
                // In a real app, we'd clone the Arc<System> here
                // For now, we just spawn a command
                Command::perform(
                                        async {
                                            // We use a fresh instance or shared ref in real code
                                            let sys = DefaultSystem::default(); 
                                            sys.run_security_scan("full").await
                                        },                    Message::ScanCompleted
                )
            }
            Message::ScanCompleted(res) => {
                self.console_log.push(format!("Scan Complete: Score {}", res.score));
                self.console_log.push(res.raw_output);
                Command::none()
            }
        }
    }

    fn view(&self) -> Element<Message> {
        // 1. Sidebar
        let sidebar = column![
            text("AEGIS").size(30).style(iced::theme::Text::Color(iced::Color::from_rgb(0.2, 0.6, 1.0))),
            button("Dashboard").on_press(Message::Tick).padding(10), // Placeholder action
            button("Security Scan").on_press(Message::RunScan).padding(10),
        ]
        .spacing(20)
        .padding(20)
        .width(Length::Fixed(200.0));

        // 2. Metrics Area
        let metrics_row = row![
            MetricCard::new("CPU Usage", self.metrics.cpu_usage, "%").view(),
            MetricCard::new("Memory", self.metrics.memory_usage, "%").view(),
            MetricCard::new("Disk", self.metrics.disk_usage, "%").view(),
        ]
        .spacing(20);

        // 3. Console Area
        let console_content = self.console_log.join("\n");
        let console = container(
            scrollable(
                text(console_content).font(iced::Font::MONOSPACE)
            )
        )
        .padding(10)
        .height(Length::Fill);

        // Layout Assembly
        let content = column![
            metrics_row,
            text("System Console").size(20),
            console
        ]
        .spacing(20)
        .padding(20);

        row![sidebar, content].into()
    }

    fn subscription(&self) -> Subscription<Message> {
        time::every(Duration::from_secs(1)).map(|_| Message::Tick)
    }
}