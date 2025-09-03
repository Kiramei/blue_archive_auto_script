#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod python_bridge;

use python_bridge::PythonBridge;

#[tauri::command]
async fn python_greet(name: String, state: tauri::State<'_, PythonBridge>) -> Result<String, String> {
  state.greet(name).await.map_err(|e| e.to_string())
}

fn main() {
  tauri::Builder::default()
    .manage(PythonBridge::default())
    .invoke_handler(tauri::generate_handler![python_greet])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
