(function($){

///////
// TEST
	this.TestChart= function(canvas) { 
		var obj = {};   
		obj.canvas = canvas;
		obj.drawTestChart = function(ss) {
			console.log (ss);
		}
		return obj;
	}
	
////////////////////////////////////////////////
//Bubble Chart
this.BubbleChart= function(canvas) { 
var obj = {};   
obj.canvas = canvas;
//var ss = {"name":"something","children":[{"name":"a","size":"5"},{"name":"b","size":"15"},{"name":"c","size":"10"}]}
obj.drawBubbleChart = function(ss) {
	//console.log ("RECEIVED ===> " + ss);
	var diameter = 350,
	format = d3.format(",d"),
	color = d3.scale.category20c();
	var bubble = d3.layout.pack()
				.sort(null)
				.size([diameter, diameter])
				.padding(1.5);
	//empty!
	$("#bubbles").empty();    
	//Generate chart
	var svg = d3.select($("#bubbles")[0]).append("svg")
			.attr("width", diameter)
			.attr("height", diameter)
			.attr("class", "bubble");
	
	var node = svg.selectAll("g.node")
			  .data(bubble.nodes(classes(ss))
			  .filter(function(d) { return !d.children; }))
			  .enter().append("g")
			  .attr("class", "node")
			  .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
	
	node.append("title")
		.text(function(d) { return d.className + ": " + format(d.value); });
	
	node.append("circle")
		.attr("r", function(d) { return d.r; })
		// option 1
		.style("fill", function (d,i) { return color(i); });
		
	node.append("text")
		.attr("dy", ".3em")
		.style("text-anchor", "middle")
		.text(function(d) { return d.className.substring(0, d.r / 3) + " (" +  d.value2 + ")";});
		//http://stackoverflow.com/questions/11007640/fit-text-into-svg-element-using-d3-js
		//.html(function(d) { return ( "<div style=mee>" + d.className.substring(0, d.r / 3) + "<br/> (" +  d.value + ")</div>" ); });
	
	//Returns a flattened hierarchy containing all leaf nodes under the root.
	function classes(ss) {
		var classes = [];
		function recurse(name, node) {
		if (node.children) {
	          node.children.forEach(function(child) { recurse(node.name, child); });
	    }
		else {
	          classes.push({packageName: name, className: node.name, value: node.size, value2: node.size2});
	     }
		}
		recurse(null, JSON.parse(ss));  
		return {children: classes};
		} //end classes()
	d3.select(self.frameElement).style("height", diameter + "px");
  }// end drawBubbleChart
	   return obj;
}  // end constructor

})(jQuery); //end
