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
//Example
//var ss = [{"name":"something","children":[{"name":"a","size":"5000","size2":"5,000" },{"name":"b","size":"15","size2":"15"}]}]
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



///////////////////////////////////////////////
//Source:http://bl.ocks.org/mbostock/3887193
this.DonutChart= function(canvas) {     
var obj = {};   
obj.canvas = canvas;
//Example
//var ss = [{"commits":"1","count":"1500","count2": "1,500"},{"commits":"2","count":"5","count2": "5"}]
//////////////////////////
obj.drawDonutChart = function(ss) {
	//console.log ("RECEIVED ===> " + ss);
      var width = 450,
      height = 200,
      radius = Math.min(width, height) / 2;
      var color = d3.scale.category20();
      var arc = d3.svg.arc()
      			.outerRadius(radius - 10)
      			.innerRadius(radius - 70);
      var pie = d3.layout.pie()
      			.sort(null)
      			.value(function(d) { return d.population; });
      
      //Generate chart
      $("#commitfrequency").empty();
      var svg = d3.select($("#commitfrequency")[0]).append("svg")
      			   .attr("width", width)
      			   .attr("height", height)
      			   .append("g")
      			   .attr("transform", "translate(" + width / 3 + "," + height / 2 + ")");

      var result = JSON.parse(ss);
      var data = [];
      for(var k in result) {
    	  data.push({"age":result[k].commits,"population":result[k].count, "count2":result[k].count2});
      }       
                      
      data.forEach(function(d) {
          d.population = +d.population;
        });   

       var fudge = -80;
       var fudge2 = 15;
       var fudge3 = -70;
       var legend = svg.selectAll("g.arc")
       .data(data)
       .enter()
       .append('g')
       .attr('class', 'legend');

       legend.append('rect')
       .attr('x', 110)
       .attr('y', function(d, i){ return ((i *  15) + fudge);})
       .attr('width', 10)
       .attr('height', 10)
       .style('fill', function(d) { 
       return color(d.age);
       });

       legend.append('text')
       .attr('x', 125)
       .attr('y', function(d, i){ return (i *  15) + fudge3;})
       .text(function(d){ return (d.age +" (" + d.count2 + ")"); });
       
       var g = svg.selectAll(".arc")
       			.data(pie(data))
       			.enter().append("svg:g")
       			.attr("class", "donutarc");

       g.append("svg:path")
       	.attr("d", arc)
       .style("fill", function(d) { return color(d.data.age); });         
 	}// end drawDonutChart
 return obj;
}  // end constructor 


               
               
})(jQuery); //end
