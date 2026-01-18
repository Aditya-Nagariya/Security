use iced::{Color, Theme, widget::{container, text, button}};

pub struct EnterpriseTheme;

impl EnterpriseTheme {
    // Matches LIGHT_THEME['accent'] from security.py (#3182CE)
    pub const ACCENT: Color = Color::from_rgb(0.19, 0.51, 0.81);
    
    // Matches LIGHT_THEME['bg_secondary'] (#F5F7FA)
    pub const BG_SECONDARY: Color = Color::from_rgb(0.96, 0.97, 0.98);
    
    pub const SUCCESS: Color = Color::from_rgb(0.22, 0.63, 0.41);
    pub const DANGER: Color = Color::from_rgb(0.90, 0.24, 0.24);
}
