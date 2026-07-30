"""
Extract CIRCLE entities from a DXF file, cluster them spatially into
per-part hole groups (since there's no layer/block separation in these
files), and report diameter distribution + spacing pattern per cluster.

This only trusts numeric geometry actually present in the file
(circle center coordinates + radius). It does NOT guess at labels,
part names, or hardware identity beyond flagging diameters that match
well-known industry-standard values for cross-reference.
"""
import sys
import math
from collections import Counter, defaultdict
import ezdxf
from ezdxf import recover

# Known standard diameters for cross-reference only (not authoritative -
# just flags for the human to confirm against real spec)
KNOWN_DIAMETERS = {
    35.0: "possible cup hinge bore",
    5.0: "possible shelf-pin hole",
    8.0: "possible dowel / KD bolt hole",
    15.0: "possible KD cam housing",
    10.0: "unidentified 10mm hole",
    11.0: "unidentified 11mm hole",
    3.0: "possible pilot hole",
    6.0: "possible pilot/shelf-pin variant",
}


def cluster_circles(circles, gap_threshold=150.0):
    """Union-find clustering: merge circles whose centers are within
    gap_threshold of each other (chained), i.e. holes belonging to the
    same physical panel will typically be much closer to each other
    than to holes on a neighbouring panel drawn elsewhere on the sheet."""
    n = len(circles)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # naive O(n^2) is fine here (a few thousand circles max per file)
    for i in range(n):
        xi, yi, _ = circles[i]
        for j in range(i + 1, n):
            xj, yj, _ = circles[j]
            if (xi - xj) ** 2 + (yi - yj) ** 2 <= gap_threshold ** 2:
                union(i, j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(circles[i])
    return list(groups.values())


def analyze_cluster(cluster):
    xs = [c[0] for c in cluster]
    ys = [c[1] for c in cluster]
    diam = Counter(round(c[2] * 2, 1) for c in cluster)
    bbox = (min(xs), min(ys), max(xs), max(ys))
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    # detect simple linear pitch: sort by x (or y if taller than wide) and
    # look at consecutive gaps among holes of the SAME diameter
    pitch_notes = []
    for d, cnt in diam.items():
        pts = sorted(
            [(c[0], c[1]) for c in cluster if round(c[2] * 2, 1) == d]
        )
        if cnt >= 3:
            # try x-direction pitch
            xs_d = sorted(set(round(p[0], 1) for p in pts))
            ys_d = sorted(set(round(p[1], 1) for p in pts))
            if len(xs_d) >= 3 and (max(xs_d) - min(xs_d)) > (max(ys_d) - min(ys_d)):
                gaps = [round(xs_d[i+1] - xs_d[i], 1) for i in range(len(xs_d)-1)]
            elif len(ys_d) >= 3:
                gaps = [round(ys_d[i+1] - ys_d[i], 1) for i in range(len(ys_d)-1)]
            else:
                gaps = []
            if gaps:
                gap_counts = Counter(gaps)
                common_gap, gap_freq = gap_counts.most_common(1)[0]
                if gap_freq >= max(2, cnt // 3):
                    pitch_notes.append(f"{d}mm holes: repeating pitch ~{common_gap}mm ({gap_freq} intervals)")

    return bbox, width, height, diam, pitch_notes


def main(path, gap_threshold=150.0, min_circles=2):
    doc, auditor = recover.readfile(path)
    msp = doc.modelspace()
    circles = [
        (round(e.dxf.center.x, 2), round(e.dxf.center.y, 2), e.dxf.radius)
        for e in msp
        if e.dxftype() == "CIRCLE"
    ]
    print(f"File: {path}")
    print(f"Total circles found: {len(circles)}\n")

    clusters = cluster_circles(circles, gap_threshold=gap_threshold)
    clusters = [c for c in clusters if len(c) >= min_circles]
    clusters.sort(key=lambda c: -len(c))

    print(f"Clustered into {len(clusters)} spatial groups (gap threshold {gap_threshold}mm, min {min_circles} circles/group)\n")
    print("=" * 70)

    for idx, cluster in enumerate(clusters, 1):
        bbox, width, height, diam, pitch_notes = analyze_cluster(cluster)
        print(f"\nGroup {idx}: {len(cluster)} holes, bounding box {width:.0f} x {height:.0f} mm")
        print(f"  Location on sheet: x[{bbox[0]:.0f},{bbox[2]:.0f}]  y[{bbox[1]:.0f},{bbox[3]:.0f}]")
        print("  Diameter breakdown:")
        for d, cnt in sorted(diam.items(), key=lambda x: -x[1]):
            note = KNOWN_DIAMETERS.get(d, "")
            note_str = f"  <-- {note}" if note else ""
            print(f"    {d:>6.1f}mm dia  x{cnt:<4d}{note_str}")
        if pitch_notes:
            print("  Spacing pattern:")
            for note in pitch_notes:
                print(f"    - {note}")


if __name__ == "__main__":
    main(sys.argv[1], gap_threshold=float(sys.argv[2]) if len(sys.argv) > 2 else 150.0)
