// Turns a resource link into a GoHighLevel tag.
// https://resources.aisavvyfounders.com/content  ->  "content"
// Only the first path segment is used; query strings and #anchors are ignored.
export const RESOURCE_HOST = "resources.aisavvyfounders.com";

export function tagFromLink(link) {
  try {
    const u = new URL(String(link).trim());
    if (u.hostname.toLowerCase() !== RESOURCE_HOST) return null;
    const slug = decodeURIComponent(u.pathname.split("/").filter(Boolean)[0] || "").trim().toLowerCase();
    return slug || null;
  } catch {
    return null;
  }
}
