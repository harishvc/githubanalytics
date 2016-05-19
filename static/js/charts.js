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



//Modified from http://jsfiddle.net/datashaman/rBfy5/show
//////////////////////////////////////////
// Horizonal Stacked Bar Chart
this.HorizontalStackedBarChart= function(canvas) { 
	var obj = {};   
	obj.canvas = canvas;
	//Example
	//var dataset   = [{"data": [{"month": "Aug","count": 123}, {"month": "Sep","count": 234}, {"month": "Oct","count": 345}],"name": "Series #4"}, 
	//                 {"data": [{"month": "Aug","count": 235}, {"month": "Sep","count": 267}, {"month": "Oct","count": 573}],"name": "Series #5"}]
	obj.drawHorizontalStackedBarChart = function(ss) {
		$("#activerepositories").empty();    
		var margins = {
			    top: 12,
			    left: 150,  //Handle long repo names!
			    right: 24,
			    bottom: 24,
			    fudge: 225
			},
			legendPanel = {
			    width: 180
			},
			width = 700 - margins.left - margins.right - legendPanel.width,
			    height = 500 - margins.top - margins.bottom - margins.fudge,
			    dataset = JSON.parse(ss),
			    series = dataset.map(function (d) {
			    	//console.log ("d.name" , d.name);
			        return d.name;
			    }),
			    dataset = dataset.map(function (d) {
			        return d.data.map(function (o, i) {
			            // Structure it so that your numeric
			            // axis (the stacked amount) is y
			            //console.log(o.count, o.month);
			        	return {
			                y: o.count,
			                x: o.reponame,
			                z: o.month
			            };
			        });
			    }),
			    stack = d3.layout.stack();

			stack(dataset);

			var dataset = dataset.map(function (group) {
			    return group.map(function (d) {
			        // Invert the x and y values, and y0 becomes x0
			    	//console.log("inverting ...", d.x,d.y,d.y0);
			        return {
			            x: d.y,
			            y: d.x,
			            z: d.z,
			            x0: d.y0
			        };
			    });
			}),
                svg = d3.select($("#activerepositories")[0])
                .append("svg")
			    .attr('width', width + margins.left + margins.right + legendPanel.width)
			        .attr('height', height + margins.top + margins.bottom)
			        .append('g')
			        .attr('transform', 'translate(' + margins.left + ',' + margins.top + ')'),
			    xMax = d3.max(dataset, function (group) {
			        return d3.max(group, function (d) {
			        	 //Convert to int
			        	 return parseInt(d.x) + parseInt(d.x0);
			        });
			    }),
			    xScale = d3.scale.linear()
			        .domain([0, xMax])
			        .range([0, width]),
			    months = dataset[0].map(function (d) { 
			    	return d.y;
			    }),
			    //_ = console.log(months),
			    
			    yScale = d3.scale.ordinal()
			        .domain(months)
			        .rangeRoundBands([0, height], .1),
			        
			    xAxis = d3.svg.axis()
			        .scale(xScale)
			        .orient('bottom'),
			        
			    //TODO: Add link    
			    yAxis = d3.svg.axis()
			        .scale(yScale)
			        .orient('left'),
			    
			    colours = d3.scale.category10(),
			    groups = svg.selectAll('g')
			        .data(dataset)
			        .enter()
			        .append('g')
			        .style('fill', function (d, i) {
			        return colours(i);
			    }),
			    rects = groups.selectAll('rect')
			        .data(function (d) {
			        return d;
			    })
			        .enter()
			        .append('rect')
			        .attr('x', function (d) {
			        return xScale(d.x0);
			    })
			        .attr('y', function (d, i) {
			        return yScale(d.y);
			    })
			        .attr('height', function (d) {
			        return yScale.rangeBand();
			    })
			        .attr('width', function (d) {
			        return xScale(d.x);
			    })
			        .on('mouseover', function (d) {
			        var xPos = parseFloat(d3.select(this).attr('x')) / 2 + width / 2;
			        var yPos = parseFloat(d3.select(this).attr('y')) + yScale.rangeBand() / 2;

			        d3.select('#tooltip')
			            .style('left', xPos + 'px')
			            .style('top', yPos + 'px')
			            .select('#value')
			            .text(d.x);
                    //TODO: Fix tooltip
			        d3.select('#tooltip').classed('hidden', false);
			    })
			        .on('mouseout', function () {
			        d3.select('#tooltip').classed('hidden', true);
			    })

			    svg.append('g')
			        .attr('class', 'axis')
			        .attr('transform', 'translate(0,' + height + ')')
			        .call(xAxis);

			svg.append('g')
			    .attr('class', 'axis')
			    .call(yAxis);

			svg.append('rect')
			    .attr('fill', 'white')
			    .attr('width', 160)
			    .attr('height', 30 * dataset.length)
			    .attr('x', width + margins.left)
			    .attr('y', 0);

			series.forEach(function (s, i) {
			    svg.append('text')
			        .attr('fill', 'black')
			        //.attr('x', width + margins.left + 8)
			        .attr('x', width + margins.left - 100 )
			        .attr('y', i * 24 + 24)
			        .text(s);
			    svg.append('rect')
			        .attr('fill', colours(i))
			        .attr('width', 60)
			        .attr('height', 20)
			        //.attr('x', width + margins.left + 90)
			         .attr('x', width +  margins.left)
			        .attr('y', i * 24 + 6);
			});
		
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
