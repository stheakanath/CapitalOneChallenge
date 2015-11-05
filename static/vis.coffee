class BubbleChart
  constructor: (data) ->
    @data = data
    @width = 940
    @height = 600

    @tooltip = CustomTooltip("gates_tooltip", 240)
    @center = {x: @width / 2, y: @height / 2}
    @layout_gravity = -0.01
    @damper = 0.1
    @vis = null
    @nodes = []
    @force = null
    @circles = null
    @fill_color = d3.scale.ordinal()
      .domain(["low", "medium", "high"])
      .range(["#d84b2a", "#909090", "#7aa25c"])
    max_amount = d3.max(@data, (d) -> parseInt(d.total_amount))
    @radius_scale = d3.scale.pow().exponent(0.5).domain([0, max_amount]).range([2, 85])
    
    this.create_nodes()
    this.create_vis()

  create_nodes: () =>
    @data.forEach (d) =>
      node = {
        id: d.id
        likes: d.likes
        radius: d.size 
        name: d.user_id
        date: d.date
        link: d.link
        group: d.group
        x: Math.random() * 900
        y: Math.random() * 800
      }
      @nodes.push node

    @nodes.sort (a,b) -> b.value - a.value

  create_vis: () =>
    @vis = d3.select("#vis").append("svg")
      .attr("width", @width)
      .attr("height", @height)
      .attr("id", "svg_vis")

    @circles = @vis.selectAll("circle")
      .data(@nodes, (d) -> d.id)

    that = this

    @circles.enter().append("circle")
      .attr("r", 0)
      .attr("fill", (d) => @fill_color(d.group))
      .attr("stroke-width", 2)
      .attr("stroke", (d) => d3.rgb(@fill_color(d.group)).darker())
      .attr("id", (d) -> "bubble_#{d.id}")
      .on("mouseover", (d,i) -> that.show_details(d,i,this))
      .on("mouseout", (d,i) -> that.hide_details(d,i,this))

    @circles.transition().duration(2000).attr("r", (d) -> d.radius)

  charge: (d) ->
    -Math.pow(d.radius, 2.0) / 8

  start: () =>
    @force = d3.layout.force()
      .nodes(@nodes)
      .size([@width, @height])

  display_group_all: () =>
    @force.gravity(@layout_gravity)
      .charge(this.charge)
      .friction(0.9)
      .on "tick", (e) =>
        @circles.each(this.move_towards_center(e.alpha))
          .attr("cx", (d) -> d.x)
          .attr("cy", (d) -> d.y)
    @force.start()

  move_towards_center: (alpha) =>
    (d) =>
      d.x = d.x + (@center.x - d.x) * (@damper + 0.02) * alpha
      d.y = d.y + (@center.y - d.y) * (@damper + 0.02) * alpha

  show_details: (data, i, element) =>
    d3.select(element).attr("stroke", "black")
    content = "<span class=\"name\">Posted By:</span><span class=\"value\"> #{data.name}</span><br/>"
    content +="<span class=\"name\">Number of Likes:</span><span class=\"value\"> #{addCommas(data.likes)}</span><br/>"
    content +="<span class=\"name\">Posted on:</span><span class=\"value\"> #{data.date}</span>"
    @tooltip.showTooltip(content,d3.event)

  hide_details: (data, i, element) =>
    d3.select(element).attr("stroke", (d) => d3.rgb(@fill_color(d.group)).darker())
    @tooltip.hideTooltip()

root = exports ? this

$ ->
  chart = null
  render_vis = (csv) ->
    chart = new BubbleChart csv
    chart.start()
    root.display_all()
  root.display_all = () =>
    chart.display_group_all()
  root.toggle_view = (view_type) =>
      root.display_all()

  d3.csv "static/data.csv", render_vis
