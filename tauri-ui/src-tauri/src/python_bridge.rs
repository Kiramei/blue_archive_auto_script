use std::process::Stdio;
use tokio::process::Command;

#[derive(Default)]
pub struct PythonBridge;

impl PythonBridge {
  pub async fn greet(&self, name: String) -> anyhow::Result<String> {
    let output = Command::new("python3")
      .arg("-c")
      .arg(format!("print('Hello, {}')", name))
      .stdout(Stdio::piped())
      .output()
      .await?;
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
  }
}
