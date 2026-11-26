// The details window sits under the list: after a selection, bring it into view if it is off screen
export function scrollToDetails() {
  requestAnimationFrame(() => {
    document.getElementById("details")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}
