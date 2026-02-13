import osmium
import sys

class XMLWriter(osmium.SimpleHandler):
    def __init__(self, f):
        super().__init__()
        self.f = f

    def node(self, n):
        # Only write generic node info
        try:
            self.f.write(f'<node id="{n.id}" lat="{n.location.lat}" lon="{n.location.lon}" version="{n.version}">')
            for t in n.tags:
                k = t.k.replace('"', '&quot;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                v = t.v.replace('"', '&quot;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                self.f.write(f'<tag k="{k}" v="{v}"/>')
            self.f.write('</node>\n')
        except Exception:
            pass # Skip invalid nodes

    def way(self, w):
        try:
            self.f.write(f'<way id="{w.id}" version="{w.version}">')
            for n in w.nodes:
                self.f.write(f'<nd ref="{n.ref}"/>')
            for t in w.tags:
                k = t.k.replace('"', '&quot;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                v = t.v.replace('"', '&quot;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                self.f.write(f'<tag k="{k}" v="{v}"/>')
            self.f.write('</way>\n')
        except Exception:
            pass

    def relation(self, r):
        pass # Skip relations to reduce size

def convert(input_file, output_file):
    print(f"Starting conversion: {input_file} -> {output_file}")
    with open(output_file, 'w', encoding='utf-8', buffering=1024*1024) as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write("<osm version='0.6' generator='python-osmium'>\n")
        
        handler = XMLWriter(f)
        # Process the file
        handler.apply_file(input_file)
        
        f.write("</osm>\n")
    print("Conversion completed.")

if __name__ == '__main__':
    convert("karachi.osm.pbf", "karachi.osm")
