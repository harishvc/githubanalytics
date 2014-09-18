function main() {
	var bubbles = BubbleChart(document.getElementById('bubbles'));
	bubbles.drawBubbleChart(LANGUAGESCOUNTARRAY);
	var donutchart = DonutChart(document.getElementById('commitfrequency'));
	donutchart.drawDonutChart(COMMITFREQUENCYARRAY);
	var hsbchart = HorizontalStackedBarChart(document.getElementById('activerepositories'));
	hsbchart.drawHorizontalStackedBarChart(ACTIVEREPOSITORIESARRAY);
}

$(document).ready(function() {
	main();
});