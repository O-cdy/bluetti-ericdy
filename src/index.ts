const PUT_ONLY_HINT = "只允许 PUT 方法上传";

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

function publicObjectUrl(base: string, key: string): string {
  const normalized = base.replace(/\/+$/, "");
  const encodedKey = key.split("/").map(encodeURIComponent).join("/");
  return `${normalized}/${encodedKey}`;
}

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return json({
        ok: true,
        service: "bluett-ericdy",
        r2Configured: Boolean(env.IMAGES),
        publicBaseConfigured: Boolean(env.PUBLIC_BASE_URL),
        timestamp: new Date().toISOString(),
      });
    }

    if (request.method !== "PUT") {
      if (url.pathname === "/" || url.pathname === "") {
        return new Response(PUT_ONLY_HINT, { status: 405 });
      }
      return new Response(PUT_ONLY_HINT, { status: 405 });
    }

    const key = url.pathname.replace(/^\/+/, "");
    if (!key) {
      return json({ message: "请在 URL 路径中指定文件名，例如 /image.png" }, 400);
    }

    if (!env.IMAGES) {
      return json(
        {
          message:
            "R2 未配置：请在 wrangler.toml 取消 [[r2_buckets]] 注释并创建 bucket 后重新部署",
        },
        503
      );
    }

    if (!env.PUBLIC_BASE_URL) {
      return json(
        {
          message:
            "PUBLIC_BASE_URL 未配置：请在 wrangler.toml 的 [vars] 中设置 R2 公网访问前缀",
        },
        503
      );
    }

    try {
      const object = await env.IMAGES.put(key, request.body, {
        httpMetadata: {
          contentType: request.headers.get("Content-Type") ?? "application/octet-stream",
        },
      });

      if (!object) {
        return json({ message: "写入 R2 失败" }, 500);
      }

      const publicUrl = publicObjectUrl(env.PUBLIC_BASE_URL, key);
      return json({
        message: "上传成功!",
        url: publicUrl,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "未知错误";
      return json({ message: `上传失败: ${message}` }, 500);
    }
  },
} satisfies ExportedHandler<Env>;
