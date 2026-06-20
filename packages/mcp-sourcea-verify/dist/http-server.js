import app from "./http-app.js";
const port = Number(process.env.PORT ?? 8787);
app.listen(port, () => {
    console.log(`sourcea-mcp-verify http listening on :${port}`);
});
