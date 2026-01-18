use ratatui::{
    prelude::*,
    widgets::*,
};
use crate::core::system::{SystemDetector, CommandResult};

pub struct OperationsState {
    pub selected_index: usize,
    pub tasks: Vec<(&'static str, &'static str)>,
    pub last_result: Option<CommandResult>,
}

impl OperationsState {
    pub fn new() -> Self {
        Self {
            selected_index: 0,
            tasks: vec![
                ("Security Scan (Lynis)", "Run full system audit"),
                ("Malware Scan (ClamAV)", "Scan /tmp for threats"),
                ("Harden SSH", "Disable Root Login"),
                ("Enable Firewall", "UFW Default Deny/Allow Out"),
            ],
            last_result: None,
        }
    }

    pub fn next(&mut self) {
        if self.selected_index < self.tasks.len() - 1 {
            self.selected_index += 1;
        }
    }

    pub fn previous(&mut self) {
        if self.selected_index > 0 {
            self.selected_index -= 1;
        }
    }

    pub fn execute_selected(&mut self, detector: &SystemDetector) {
        let result = match self.selected_index {
            0 => detector.scan_lynis(),
            1 => detector.scan_clamav(),
            2 => detector.harden_ssh(),
            3 => detector.enable_firewall(),
            _ => return,
        };
        self.last_result = Some(result);
    }
}

pub fn draw_operations(f: &mut Frame, area: Rect, state: &OperationsState) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(area);

    // List
    let items: Vec<ListItem> = state.tasks
        .iter()
        .enumerate()
        .map(|(i, (title, _))| {
            let style = if i == state.selected_index {
                Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::Gray)
            };
            ListItem::new(format!("> {}", title)).style(style)
        })
        .collect();

    let list = List::new(items)
        .block(Block::default().borders(Borders::ALL).title(" OPERATIONS "));
    f.render_widget(list, chunks[0]);

    // Detail / Output
    let output_text = if let Some(res) = &state.last_result {
        let color = if res.success { Color::Green } else { Color::Red };
        vec![
            Line::from(vec![
                Span::styled(if res.success { "SUCCESS" } else { "FAILURE" }, Style::default().fg(color).add_modifier(Modifier::BOLD)),
                Span::raw(format!(" ({:.2}s)", res.duration))
            ]),
            Line::from(""),
            Line::from(res.stdout.as_str()),
            Line::from(res.stderr.as_str()),
        ]
    } else {
        let (_, desc) = state.tasks[state.selected_index];
        vec![
            Line::from(Span::styled("READY", Style::default().fg(Color::Cyan))),
            Line::from(""),
            Line::from(desc),
            Line::from(""),
            Line::from(Span::styled("Press [ENTER] to execute", Style::default().fg(Color::DarkGray))),
        ]
    };

    let p = Paragraph::new(output_text)
        .block(Block::default().borders(Borders::ALL).title(" OUTPUT "))
        .wrap(Wrap { trim: true });
    f.render_widget(p, chunks[1]);
}
