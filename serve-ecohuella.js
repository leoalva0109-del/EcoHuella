const http = require("http");
const fs = require("fs");
const path = require("path");

const root = __dirname;
const port = Number(process.env.PORT || 8080);
const host = "0.0.0.0";

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".avif": "image/avif",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".mp4": "video/mp4",
  ".webm": "video/webm"
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "X-Content-Type-Options": "nosniff"
  });
  res.end(body);
}

function resolveRequest(url) {
  const requestPath = decodeURIComponent(new URL(url, "http://localhost").pathname);
  const cleanPath = requestPath === "/" ? "/index.html" : requestPath;
  const relativePath = cleanPath.replace(/^\/+/, "");

  if (relativePath.includes("..") || relativePath.startsWith(".vscode")) {
    return null;
  }

  const extension = path.extname(relativePath).toLowerCase();
  const allowed =
    ["index.html", "fases.html", "ia.html", "tecnico.html", "materiales.html", "metodologia.html", "diagramas.html", "styles.css", "script.js"].includes(relativePath) ||
    (relativePath.startsWith("assets/") && Boolean(mimeTypes[extension]));

  if (!allowed) {
    return null;
  }

  const filePath = path.join(root, relativePath);
  return filePath.startsWith(root) ? filePath : null;
}

const server = http.createServer((req, res) => {
  const filePath = resolveRequest(req.url);

  if (!filePath) {
    send(res, 404, "Archivo no publicado.");
    return;
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      send(res, error.code === "ENOENT" ? 404 : 500, "No se pudo cargar el archivo.");
      return;
    }

    send(res, 200, data, mimeTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream");
  });
});

server.listen(port, host, () => {
  console.log(`EcoHuella IA-Bio disponible en http://localhost:${port}`);
});
