import os
import numpy as np
import matplotlib.pyplot as plt
import pylab
# color palette
from matplotlib import cm
from logsparser.lognormalizer import LogNormalizer as LN
import GeoIP
 
normalizer = LN('/home/kura//.virtualenvs/ssh-attack-visualisation/share/logsparser/normalizers/')
auth_logs = open('/home/kura/workspace/ssh-attack-visualisation/logs/auth.log.combined', 'r')
locator = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
 
dataset = {}
for log in auth_logs:
    l = {'raw' : log[:-1] } # remove the ending \n
    normalizer.normalize(l)
    if l.get('action') == 'fail':
        key = str(l['date'].hour).rjust(2,'0') +\
              str(l['date'].minute).rjust(2,'0') +\
              str(l['date'].second).rjust(2,'0')
        dataset[key] = dataset.get(key, {})
        country_l = locator.country_code_by_addr(l['source_ip'])
        if country_l:
            country = country_l
        else:
            country = "Unknown"
        dataset[key][country] = dataset[key].get(country, 0) + 1

from mpl_toolkits.basemap import Basemap
 
def makemap():
    m = Basemap(projection="merc",
                llcrnrlat=-70,
                urcrnrlat=78,
                llcrnrlon=-180,
                urcrnrlon=180,
                lat_ts=20,
                resolution='c')
    m.drawcoastlines(color="white")
    m.drawmapboundary(fill_color="black")
    m.drawcountries(linewidth = 0.3, color = "white")
    return m

from shapelib import ShapeFile
import dbflib
from matplotlib.collections import LineCollection
 
class CountryDrawer:
    def __init__(self,
                 shpfile = "worldmap/TM_WORLD_BORDERS-0.3.shp",
                 dbffile = "worldmap/TM_WORLD_BORDERS-0.3.dbf"):
        shp = ShapeFile(shpfile)
        dbf = dbflib.open(dbffile)
        self.countries = {}
        for i in range(shp.info()[0]):
            c = dbf.read_record(i)['ISO2']
            poly = shp.read_object(i)
            self.countries[c] = poly.vertices()
 
    def drawcountry(self,
                    ax,
                    base_map,
                    iso2,
                    color,
                    alpha = 1):
        if iso2 not in self.countries:
            raise ValueError, "Where is that country ?"
        vertices = self.countries[iso2]
        shape = []
        for vertex in vertices:
            longs, lats = zip(*vertex)
            # conversion to plot coordinates
            x,y = base_map(longs, lats)
            shape.append(zip(x,y))
        lines = LineCollection(shape,antialiaseds=(1,))
        lines.set_facecolors(cm.hot(np.array([color,])))
        lines.set_edgecolors('white')
        lines.set_linewidth(0.5)
        lines.set_alpha(alpha)
        ax.add_collection(lines)


if __name__ == "__main__":
    cd = CountryDrawer()
    currentkey = "0000"
    alpha = 1
    i = 0

    for key in sorted(dataset.keys()):
        if os.path.exists("rendering/plot%s.png" % str(i+1).rjust(5,'0')):
            i += 1
            print "exists, skip"
            continue
        fig = plt.figure(figsize=(6.2,3.6))
        plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
        ax = plt.subplot(111)
        m = makemap()
        data = dataset[key]
        total_attacks = float(sum(data.values()))
#        if key in dataset:
#            alpha = 1
#        else:
#            alpha *= 0.7
        for c in data:
            if c != 'Unknown':
                color = 0.2
#                color = 0.6*data[c]/total_attacks
                cd.drawcountry(ax, m, c, color, alpha )
        plt.text(50,50,"%s:%s:%s" % (key[0:2], key[2:4], key[4:]), color = 'white', size=16)
        plt.savefig('rendering/plot%s.png' % str(i+1).rjust(5,'0'), dpi=200)
        pylab.close(fig)
        i += 1
