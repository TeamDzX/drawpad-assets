"""
Prompt specs for the ComfyUI-generated packs (coloring + mandala).

Style strings are locked per category so a pack generated six months from now
still sits next to the launch packs without looking like a different app.
Keep additions inside these two dicts rather than passing ad-hoc prompts —
the pipeline is only reproducible if the prompt lives in the repo.
"""

# Shared tail. "no text" matters: Flux will happily letter a sign or a birthday
# cake, and the app has no way to erase it.
BASE = ("black and white coloring book page, thick clean black outlines, "
        "uniform line weight, outline drawing only, every shape left empty "
        "and white inside, no solid black areas, no filled shapes, no "
        "silhouettes, no shading, no hatching, no grey, no fill, no colour, "
        "pure white background, centered composition, no text, "
        "no watermark, no signature")

# Kids' coloring pages: bold lines a fat brush can stay inside of.
COLORING = ("%s, simple friendly cartoon style for young children, "
            "single subject, full body, generous white space, "
            "original character design not based on any existing franchise"
            % BASE)

# Mandalas: finer lines, symmetry is the whole point.
MANDALA = ("%s, intricate symmetrical mandala, perfectly radially symmetric, "
           "concentric rings of ornamental motifs, thin precise linework, "
           "fills the circular frame" % BASE)

COLORING_PACKS = [
    dict(id="coloring_dinosaurs", title="Dino Days",
         subtitle="8 friendly dinosaurs to color",
         pages=[
             ("01", "T-Rex", "a friendly cartoon tyrannosaurus rex standing and smiling, short arms, rounded body"),
             ("02", "Triceratops", "a cute cartoon triceratops with three horns and a neck frill, standing side on"),
             ("03", "Stegosaurus", "a cute cartoon stegosaurus with large back plates and a spiked tail, walking"),
             ("04", "Long Neck", "a cute cartoon brachiosaurus with a very long neck reaching up to a leafy branch"),
             ("05", "Sky Wings", "a cute cartoon pterodactyl with spread wings gliding, seen from the side"),
             ("06", "Little Raptor", "a small friendly cartoon raptor dinosaur running, feathered tail"),
             ("07", "Club Tail", "a chubby cartoon ankylosaurus with an armoured back and a round club tail"),
             ("08", "Hatchling", "a baby cartoon dinosaur hatching out of a cracked egg, big happy eyes"),
         ]),
    dict(id="coloring_ocean", title="Under the Sea",
         subtitle="8 sea creatures to color",
         pages=[
             ("01", "Dolphin", "a happy cartoon dolphin leaping above a simple wave"),
             ("02", "Octopus", "a cheerful cartoon octopus with eight curling tentacles and big round eyes"),
             ("03", "Seahorse", "a cute cartoon seahorse with a curled tail beside two strands of seaweed"),
             ("04", "Whale", "a friendly cartoon whale spouting water, rounded body, small eye"),
             ("05", "Starfish", "a smiling cartoon starfish resting on the sea floor with two small shells"),
             ("06", "Crab", "a cheerful cartoon crab with two big claws walking on sand"),
             ("07", "Jellyfish", "a cute cartoon jellyfish with a domed bell and long wavy tentacles"),
             ("08", "Clownfish", "a cartoon clownfish with wide stripes swimming beside a sea anemone"),
         ]),
    dict(id="coloring_space", title="Blast Off",
         subtitle="8 space adventures to color",
         pages=[
             ("01", "Rocket", "a cartoon rocket ship blasting upward with rounded flames below, round window"),
             ("02", "Astronaut", "a cute cartoon astronaut floating in a spacesuit and round helmet, waving"),
             ("03", "Ringed Planet", "a cartoon planet with a wide tilted ring, surrounded by simple stars"),
             ("04", "Friendly Alien", "a small friendly cartoon alien with big eyes and two antennae, waving"),
             ("05", "Moon Landing", "a cartoon lunar lander on a cratered moon surface with a small flag, no text"),
             ("06", "Space Buggy", "a cartoon moon rover with chunky wheels driving over craters"),
             ("07", "Satellite", "a cartoon satellite with two solar panel wings and a dish antenna in space"),
             ("08", "Shooting Star", "a smiling cartoon shooting star with a long curved trail and small stars"),
         ]),
    dict(id="coloring_treats", title="Sweet Treats",
         subtitle="8 tasty treats to color",
         pages=[
             ("01", "Cupcake", "a cartoon cupcake with a tall swirl of frosting and a cherry on top"),
             ("02", "Ice Cream", "a cartoon ice cream cone with three round scoops and a drip"),
             ("03", "Donut", "a cartoon ring donut with drizzled icing and round sprinkles"),
             ("04", "Cookie", "a large cartoon chocolate chip cookie with a bite taken out"),
             ("05", "Birthday Cake", "a cartoon two tier birthday cake with candles and simple bunting, no text"),
             ("06", "Lollipop", "a cartoon swirl lollipop on a stick with a small ribbon bow"),
             ("07", "Pancakes", "a cartoon stack of pancakes with a pat of butter and syrup pouring"),
             ("08", "Fruit Bowl", "a cartoon bowl of fruit with an apple, a pear, a banana and grapes"),
         ]),
    dict(id="coloring_fairytale", title="Once Upon a Time",
         subtitle="8 fairy tale scenes to color",
         pages=[
             ("01", "Castle", "a cartoon fairy tale castle with three round towers and pointed roofs and a gate"),
             ("02", "Friendly Dragon", "a small friendly cartoon dragon with little wings sitting and smiling"),
             ("03", "Brave Knight", "a cartoon knight in simple armour holding a round shield, original design"),
             ("04", "Wizard", "a tall kindly cartoon wizard in a long flowing floor length robe with wide sleeves, a large wide brimmed pointed hat and a tall staff, long beard, original design, not a gnome, not a dwarf"),
             ("05", "Mermaid", "a cartoon mermaid with a long curling tail sitting on a rock, original design"),
             ("06", "Fairy", "a small cartoon fairy with round wings hovering over a flower, original design"),
             ("07", "Magic Book", "an open cartoon spell book with stars and swirls rising from the pages, no text"),
             ("08", "Toadstool House", "a cartoon toadstool cottage with a round door, small windows and a path"),
         ]),
    dict(id="coloring_farm", title="Down on the Farm",
         subtitle="8 farm friends to color",
         pages=[
             ("01", "Cow", "a friendly cartoon cow standing side on with a patched coat and a bell collar"),
             ("02", "Pig", "a chubby happy cartoon pig standing side on with a curly tail"),
             ("03", "Sheep", "a fluffy cartoon sheep with a woolly coat standing in short grass"),
             ("04", "Horse", "a friendly cartoon horse standing side on with a flowing mane and tail"),
             ("05", "Chicken", "a plump cartoon hen pecking, with a comb and tail feathers"),
             ("06", "Goat", "a cheerful cartoon goat with small curved horns and a little beard"),
             ("07", "Barn", "a cartoon barn with big double doors, a hayloft window and a weather vane"),
             ("08", "Scarecrow", "a friendly cartoon scarecrow on a post with a straw hat and patched clothes"),
         ]),
    dict(id="coloring_jungle", title="Jungle Friends",
         subtitle="8 jungle animals to color",
         pages=[
             ("01", "Monkey", "a cheeky cartoon monkey hanging from a branch by one arm"),
             ("02", "Tiger", "a friendly cartoon tiger sitting, with bold stripes and a round face"),
             ("03", "Parrot", "a cartoon parrot perched on a branch with a curved beak and long tail feathers"),
             ("04", "Snake", "a smiling cartoon snake coiled in loops with a patterned back"),
             ("05", "Crocodile", "a friendly cartoon crocodile lying down with a long snout and bumpy back"),
             ("06", "Hippo", "a chubby happy cartoon hippo standing in shallow water"),
             ("07", "Zebra", "a cartoon zebra standing side on with an upright mane, its stripes drawn as empty outlined bands with white interiors, no black fill anywhere"),
             ("08", "Toucan", "a cartoon toucan perched on a branch with a very large curved beak"),
         ]),
]

MANDALA_PACKS = [
    dict(id="mandala_geometric", title="Geometric Mandalas",
         subtitle="8 geometric mandalas",
         pages=[
             ("01", "Hexagon", "built from nested hexagons and triangles, six fold symmetry"),
             ("02", "Lattice", "an interlocking woven square lattice of broad bands forming large open cells, eight fold symmetry, bold spacious shapes, few rings"),
             ("03", "Kaleidoscope", "sharp kaleidoscope shards radiating outward, twelve fold symmetry"),
             ("04", "Prism", "concentric rings of diamonds and chevrons, eight fold symmetry"),
             ("05", "Spiral", "a geometric spiral of repeating squares turning around the centre"),
             ("06", "Mosaic", "small mosaic tiles arranged in concentric circular bands"),
             ("07", "Compass", "a compass rose of long pointed rays with an ornate centre, eight fold symmetry"),
             ("08", "Weave", "an over and under woven basket pattern in a circular frame"),
         ]),
    dict(id="mandala_animals", title="Animal Mandalas",
         subtitle="8 animal mandalas",
         pages=[
             ("01", "Elephant", "an ornate elephant head at the centre framed by radiating decorative petals"),
             ("02", "Owl", "a decorative owl at the centre with radiating feather patterns forming the rings"),
             ("03", "Butterfly", "a symmetrical butterfly at the centre with ornamental wing patterning"),
             ("04", "Turtle", "a sea turtle at the centre, its shell segments echoed in the outer rings"),
             ("05", "Lion", "a lion head at the centre with a radiating ornamental mane"),
             ("06", "Wolf", "a symmetrical wolf head at the centre framed by radiating geometric rays"),
             ("07", "Peacock", "a peacock with a radiating fan of ornate tail feathers, perfectly symmetric"),
             ("08", "Dragonfly", "four symmetrical dragonfly wings radiating from an ornate centre"),
         ]),
    dict(id="mandala_celtic", title="Celtic Knots",
         subtitle="8 knotwork mandalas",
         pages=[
             ("01", "Trinity", "a celtic triquetra knot at the centre, three fold symmetry, continuous interlaced bands"),
             ("02", "Endless Knot", "an endless celtic knot of interlaced bands in a circular frame"),
             ("03", "Braid Ring", "three broad celtic braid bands with large open cells, over and under weaving, bold spacious knotwork, plain centre"),
             ("04", "Cross", "a celtic ring cross with interlaced knotwork panels"),
             ("05", "Spiral Triad", "three celtic spirals radiating from the centre with knotwork borders"),
             ("06", "Shield Knot", "a square celtic shield knot inside a circular knotwork border"),
             ("07", "Vine Knot", "interlaced celtic vines and leaves woven into a circular knot"),
             ("08", "Serpent", "two interlaced celtic serpents forming a symmetrical circular knot"),
         ]),
    dict(id="mandala_seasons", title="Seasons Mandalas",
         subtitle="8 mandalas through the year",
         pages=[
             ("01", "Spring Blossom", "cherry blossom flowers and buds radiating in concentric rings"),
             ("02", "Summer Sun", "a radiant sun with long and short rays and an ornate face-free centre"),
             ("03", "Autumn Leaf", "maple and oak leaves radiating outward in concentric rings"),
             ("04", "Snowflake", "an intricate six fold snowflake mandala with crystalline branches"),
             ("05", "Rain", "large teardrop and raindrop motifs radiating outward like petals, bold spacious shapes, few concentric rings"),
             ("06", "Harvest", "wheat sheaves, berries and seeds radiating in concentric rings"),
             ("07", "Frost", "delicate frost crystal ferns radiating from the centre, six fold symmetry"),
             ("08", "Midsummer", "sunflowers and long leaves radiating outward, eight fold symmetry"),
         ]),
    dict(id="mandala_butterflies", title="Butterfly Mandalas",
         subtitle="8 butterfly and wing mandalas",
         pages=[
             ("01", "Monarch", "four symmetrical butterfly wings radiating from an ornate centre, the wing markings drawn as empty outlined cells with white interiors, stained glass style, no black fill anywhere"),
             ("02", "Swallowtail", "swallowtail butterflies with long tailed wings arranged in a ring"),
             ("03", "Wing Lace", "a single large symmetrical butterfly with lace patterned wings filling the circle"),
             ("04", "Flutter", "eight small butterflies radiating outward around a floral centre"),
             ("05", "Moth", "a symmetrical moth with feathered antennae and patterned wings, ornate border"),
             ("06", "Chrysalis", "chrysalises and leaves radiating in concentric rings around a butterfly centre"),
             ("07", "Meadow", "butterflies and wildflowers alternating in concentric rings"),
             ("08", "Wingspan", "two large mirrored butterfly wings forming a circular mandala, ornate scales"),
         ]),
    dict(id="mandala_lace", title="Lace Mandalas",
         subtitle="8 delicate lace mandalas",
         pages=[
             ("01", "Doily", "a crocheted doily pattern with scalloped edges and open lace work"),
             ("02", "Filigree", "fine metal filigree scrollwork radiating in concentric rings"),
             ("03", "Snow Lace", "a lace snowflake with delicate crystalline branches, six fold symmetry"),
             ("04", "Scallop", "concentric rings of scalloped lace edging with small open eyelets"),
             ("05", "Ribbon", "interwoven lace ribbons looping around a circular frame"),
             ("06", "Rosette", "a lace rosette of layered petals with picot edging"),
             ("07", "Web", "a fine lace web of radiating threads and knotted joins, twelve fold symmetry"),
             ("08", "Damask", "a damask lace pattern of leaves and scrolls in concentric bands"),
         ]),
]


def prompt_for(kind, page_prompt):
    return "%s, %s" % (page_prompt, COLORING if kind == "coloring" else MANDALA)
