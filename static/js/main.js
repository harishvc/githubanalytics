function main() {
	var bubbles = BubbleChart(document.getElementById('bubbles'));
	bubbles.drawBubbleChart(LANGUAGESCOUNTARRAY);
	var donutchart = DonutChart(document.getElementById('commitfrequency'));
	donutchart.drawDonutChart(COMMITFREQUENCYARRAY);
}

$(document).ready(function() {
	main();
});