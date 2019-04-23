all: tomaszcichocki2.svg

clean:
	rm *-solution.json *-base.json *.svg

t2-solution.json: t2.json
	./mip.py $^

t2-base.json: t2-solution.json
	./filter_coordinates.py $^ : :

o2-solution.json: o2.json t2-base.json
	./mip.py $^

to2-solution.json: t2-solution.json o2-solution.json
	./stitch.py $^ $@

to2-base.json: to2-solution.json
	./filter_coordinates.py $^ : :

m2-solution.json: m2.json to2-base.json
	./mip.py $^

tom2-solution.json: to2-solution.json m2-solution.json
	./stitch.py $^ $@

tom2-base.json: tom2-solution.json
	./filter_coordinates.py $^ 300: :

a2-solution.json: a2.json tom2-base.json
	./mip.py $^

toma2-solution.json: tom2-solution.json a2-solution.json
	./stitch.py $^ $@

toma2-base.json: toma2-solution.json
	./filter_coordinates.py $^ 550: :

s2-solution.json: s2.json toma2-base.json
	./mip.py $^

tomas2-solution.json: toma2-solution.json s2-solution.json
	./stitch.py $^ $@

tomas2-base.json: tomas2-solution.json
	./filter_coordinates.py $^ 600: :

tomas2.svg: tomas2-solution.json
	./svg.py $^

z2-solution.json: z2.json tomas2-base.json
	./mip.py $^

tomasz2-solution.json: tomas2-solution.json z2-solution.json
	./stitch.py $^ $@

tomasz2.svg: tomasz2-solution.json
	./svg.py $^

tomasz2-base.json: tomasz2-solution.json
	./filter_coordinates.py $^ 700: :

c2-solution.json: c2.json tomasz2-base.json
	./mip.py $^

tomaszc2-solution.json: tomasz2-solution.json c2-solution.json
	./stitch.py $^ $@

tomaszc2.svg: tomaszc2-solution.json
	./svg.py $^

tomaszc2-base.json: tomaszc2-solution.json
	./filter_coordinates.py $^ 800: :

i2-solution.json: i2.json tomaszc2-base.json
	./mip.py $^

tomaszci2-solution.json: tomaszc2-solution.json i2-solution.json
	./stitch.py $^ $@

tomaszci2.svg: tomaszci2-solution.json
	./svg.py $^

tomaszci2-base.json: tomaszci2-solution.json
	./filter_coordinates.py $^ 850: :

c3-solution.json: c3.json tomaszci2-base.json
	./mip.py $^

tomaszcic2-solution.json: tomaszci2-solution.json c3-solution.json
	./stitch.py $^ $@

tomaszcic2.svg: tomaszcic2-solution.json
	./svg.py $^

tomaszcic2-base.json: tomaszcic2-solution.json
	./filter_coordinates.py $^ 950: :

h2-solution.json: h2.json tomaszcic2-base.json
	./mip.py $^

tomaszcich2-solution.json: tomaszcic2-solution.json h2-solution.json
	./stitch.py $^ $@

tomaszcich2.svg: tomaszcich2-solution.json
	./svg.py $^

tomaszcich2-base.json: tomaszcich2-solution.json
	./filter_coordinates.py $^ 1250: :

o3-solution.json: o3.json tomaszcich2-base.json
	./mip.py $^

tomaszcicho2-solution.json: tomaszcich2-solution.json o3-solution.json
	./stitch.py $^ $@

tomaszcicho2.svg: tomaszcicho2-solution.json
	./svg.py $^

tomaszcicho2-base.json: tomaszcicho2-solution.json
	./filter_coordinates.py $^ 1350: :

c4-solution.json: c4.json tomaszcicho2-base.json
	./mip.py $^

tomaszcichoc2-solution.json: tomaszcicho2-solution.json c4-solution.json
	./stitch.py $^ $@

tomaszcichoc2.svg: tomaszcichoc2-solution.json
	./svg.py $^

tomaszcichoc2-base.json: tomaszcichoc2-solution.json
	./filter_coordinates.py $^ 1480: :

k2-solution.json: k2.json tomaszcichoc2-base.json
	./mip.py $^

tomaszcichock2-solution.json: tomaszcichoc2-solution.json k2-solution.json
	./stitch.py $^ $@

tomaszcichock2.svg: tomaszcichock2-solution.json
	./svg.py $^

tomaszcichock2-base.json: tomaszcichock2-solution.json
	./filter_coordinates.py $^ 1900: 200:

i3-solution.json: i3.json tomaszcichock2-base.json
	./mip.py $^

tomaszcichocki2-solution.json: tomaszcichock2-solution.json i3-solution.json
	./stitch.py $^ $@

tomaszcichocki2.svg: tomaszcichocki2-solution.json
	./svg.py $^
