use iced::widget::{column, container, text, ProgressBar, row};
use iced::{Element, Length, Alignment};
use crate::ui::theme::EnterpriseTheme;

pub struct MetricCard {
    label: String,
    value: f32,
    unit: String,
}

impl MetricCard {
    pub fn new(label: impl Into<String>, value: f32, unit: impl Into<String>) -> Self {
        Self {
            label: label.into(),
            value,
            unit: unit.into(),
        }
    }

    pub fn view<'a, Message: 'a>(&self) -> Element<'a, Message> {
        let label = text(&self.label).size(14);
        let value_text = text(format!("{:.1}{}", self.value, self.unit)).size(24);
        
        let bar = ProgressBar::new(0.0..=100.0, self.value)
            .height(Length::Fixed(8.0));

        container(
            column![
                row![label, value_text].spacing(10).align_items(Alignment::Center),
                bar
            ]
            .spacing(10)
        )
        .padding(15)
        .into()
    }
}
