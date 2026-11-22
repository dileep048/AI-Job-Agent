import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { buildJobSearchQuery } from "./jobSearchQuery.ts";

describe("buildJobSearchQuery", () => {
  it("omits empty filters", () => {
    assert.equal(buildJobSearchQuery({ q: "", location: undefined }), "");
  });

  it("encodes search, filters, and pagination", () => {
    const query = buildJobSearchQuery({
      q: "python",
      location: "bangalore",
      workplace_type: "remote",
      page: 2,
      page_size: 20,
      is_active: true,
    });
    assert.ok(query.includes("q=python"));
    assert.ok(query.includes("location=bangalore"));
    assert.ok(query.includes("workplace_type=remote"));
    assert.ok(query.includes("page=2"));
    assert.ok(query.includes("page_size=20"));
    assert.ok(query.includes("is_active=true"));
    assert.ok(query.startsWith("?"));
  });
});
