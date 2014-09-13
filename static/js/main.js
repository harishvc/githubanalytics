function main() {
	var bubbles = BubbleChart(document.getElementById('bubbles'));
	bubbles.drawBubbleChart(LANGUAGESCOUNTARRAY);
}

$(document).ready(function() {
	main();
});