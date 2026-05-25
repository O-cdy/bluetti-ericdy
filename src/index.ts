export default {
  async fetch(request: Request, _env: Env, _ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        service: "bluett-ericdy",
        timestamp: new Date().toISOString(),
      });
    }

    if (url.pathname === "/" || url.pathname === "") {
      return new Response("bluett-ericdy worker is running", {
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }

    return new Response("Not Found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
