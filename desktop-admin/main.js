const fs = require("fs");
const path = require("path");
const { app, BrowserWindow, Menu, shell } = require("electron");

const rootDir = path.resolve(__dirname, "..");
const urlFile = path.join(rootDir, "admin-panel-url.txt");

function adminUrl() {
  let url = "http://127.0.0.1:8088";
  try {
    const configured = fs.readFileSync(urlFile, "utf8").trim();
    if (configured) url = configured;
  } catch (error) {
    // Local fallback is useful for development if the URL file is not present.
  }
  if (!url.endsWith("/login")) {
    url = url.replace(/\/+$/, "") + "/login";
  }
  return url;
}

function createWindow() {
  Menu.setApplicationMenu(null);
  const win = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 960,
    minHeight: 680,
    title: "Visa eSIM Admin Panel",
    backgroundColor: "#f5f7fb",
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  win.loadURL(adminUrl()).catch((error) => {
    win.loadURL("data:text/html;charset=utf-8," + encodeURIComponent(`
      <html>
        <head><title>Visa eSIM Admin Panel</title></head>
        <body style="font-family:Arial,sans-serif;padding:32px;background:#f5f7fb;color:#172033">
          <h2>Admin panel ochilmadi</h2>
          <p>Render URL yoki internet ulanishini tekshiring.</p>
          <p><b>URL:</b> ${adminUrl()}</p>
          <pre style="white-space:pre-wrap;background:white;border:1px solid #dde3ee;padding:12px;border-radius:8px">${error.message}</pre>
        </body>
      </html>
    `));
  });
}

app.setName("Visa eSIM Admin Panel");

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
