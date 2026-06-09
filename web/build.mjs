import { writeFileSync } from "node:fs";

const DEFAULT_API_URL = "https://sqwash-pdf-api.onrender.com";
const apiUrl = (process.env.API_URL || DEFAULT_API_URL).replace(/\/$/, "");

const vercelJson = {
  outputDirectory: ".",
  rewrites: [
    {
      source: "/api/:path*",
      destination: `${apiUrl}/api/:path*`,
    },
  ],
};

const configJs = `window.SQWASH_CONFIG = {
  apiBase: ""
};
`;

writeFileSync("vercel.json", `${JSON.stringify(vercelJson, null, 2)}\n`);
writeFileSync("config.js", configJs);

console.log(`Build complete. API rewrite target: ${apiUrl}`);
