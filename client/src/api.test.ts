import { describe, expect, it } from "vitest";
import { buildUrl } from "./api";

describe("buildUrl", () => {
  it("joint base et chemin sans double slash", () => {
    expect(buildUrl("https://api.example.com/", "/health")).toBe("https://api.example.com/health");
  });
  it("échoue si VITE_API_URL est absente", () => {
    expect(() => buildUrl(undefined, "/health")).toThrow();
  });
});
