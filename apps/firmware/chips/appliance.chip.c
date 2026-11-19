// Simulator-only appliance graphics. SW observes the relay's NO contact.
// kind: 0 = lighting, 1 = fan, 2 = cooling. No energy/thermal model here.
#include "wokwi-api.h"

#define WIDTH 240
#define HEIGHT 160
#define RGB(r,g,b) ((uint32_t)(r) | ((uint32_t)(g)<<8) | ((uint32_t)(b)<<16) | 0xff000000u)
#define BG RGB(17,27,43)
#define INK RGB(224,234,244)
#define MUTED RGB(95,118,144)
#define EDGE RGB(44,65,89)

typedef struct {
  pin_t switched;
  buffer_t display;
  uint32_t kind;
  uint32_t frame;
  bool on;
  uint32_t pixels[WIDTH * HEIGHT];
} appliance_t;

// Wokwi can share one WASM module across instances. Allocate separate state
// for each of this circuit's three appliances, without a libc/WASI dependency.
static appliance_t appliances[3];
static uint32_t appliance_count;

static int magnitude(int value) { return value < 0 ? -value : value; }

static void pixel(appliance_t *s, int x, int y, uint32_t color) {
  if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT)
    s->pixels[y * WIDTH + x] = color;
}

static void box(appliance_t *s, int x, int y, int w, int h, uint32_t color) {
  for (int j = y; j < y+h; j++)
    for (int i = x; i < x+w; i++) pixel(s, i, j, color);
}

static void disc(appliance_t *s, int cx, int cy, int radius, uint32_t color) {
  for (int y = -radius; y <= radius; y++)
    for (int x = -radius; x <= radius; x++)
      if (x*x+y*y <= radius*radius) pixel(s, cx+x, cy+y, color);
}

static void line(appliance_t *s, int x0, int y0, int x1, int y1, uint32_t color) {
  int dx = magnitude(x1-x0), sx = x0 < x1 ? 1 : -1;
  int dy = -magnitude(y1-y0), sy = y0 < y1 ? 1 : -1, err = dx+dy;
  for (;;) {
    pixel(s, x0, y0, color);
    if (x0 == x1 && y0 == y1) break;
    int e2 = 2*err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
}

// Compact 5x7 lettering for the persistent ON/OFF badge.
static void glyph(appliance_t *s, int x, int y, char c, uint32_t color) {
  static const uint8_t o[] = {14,17,17,17,17,17,14};
  static const uint8_t n[] = {17,25,25,21,19,19,17};
  static const uint8_t f[] = {31,16,16,30,16,16,16};
  const uint8_t *rows = c == 'O' ? o : c == 'N' ? n : f;
  for (int row = 0; row < 7; row++)
    for (int col = 0; col < 5; col++)
      if (rows[row] & (1 << (4-col))) box(s, x+col*2, y+row*2, 2, 2, color);
}

static void render(appliance_t *s) {
  box(s, 0, 0, WIDTH, HEIGHT, BG);
  box(s, 0, 0, WIDTH, 3, s->on ? RGB(61,213,172) : EDGE);
  if (s->kind == 0) {
    // Suspended classroom light with two illuminated tubes.
    line(s, 65, 15, 65, 41, MUTED);
    line(s, 175, 15, 175, 41, MUTED);
    if (s->on) {
      for (int y = 74; y < 119; y++)
        box(s, 39-(y-74)/3, y, 162+2*((y-74)/3), 1, RGB(42,43,35));
      for (int x = 55; x <= 185; x += 26) line(s, x, 85, x, 107, RGB(169,148,67));
    }
    box(s, 30, 41, 180, 39, MUTED);
    box(s, 36, 47, 168, 27, EDGE);
    box(s, 43, 51, 154, 7, s->on ? RGB(255,245,177) : MUTED);
    box(s, 43, 63, 154, 7, s->on ? RGB(255,245,177) : MUTED);
  } else if (s->kind == 1) {
    // Four animated blades, enclosed by a circular fan guard.
    static const int sine[] = {0,38,71,92,100,92,71,38,0,-38,-71,-92,-100,-92,-71,-38};
    box(s, 114, 100, 12, 20, MUTED);
    box(s, 89, 117, 62, 5, MUTED);
    disc(s, 120, 65, 51, MUTED);
    disc(s, 120, 65, 47, BG);
    for (int b = 0; b < 4; b++) {
      int a = (s->frame + b*4) % 16;
      int cx = 120 + sine[(a+4)%16]*27/100;
      int cy = 65 + sine[a]*27/100;
      line(s, 120, 65, cx, cy, MUTED);
      disc(s, cx, cy, 16, s->on ? RGB(61,213,172) : MUTED);
    }
    disc(s, 120, 65, 10, INK);
    line(s, 72, 65, 168, 65, EDGE);
    line(s, 120, 17, 120, 113, EDGE);
    disc(s, 120, 65, 5, INK);
  } else {
    // Wall-mounted cooling unit; airflow moves only while switched on.
    box(s, 24, 24, 192, 62, MUTED);
    box(s, 28, 28, 184, 54, INK);
    box(s, 39, 39, 162, 18, RGB(192,208,222));
    box(s, 39, 63, 162, 14, EDGE);
    for (int x = 44; x < 199; x += 10) box(s, x, 66, 5, 8, MUTED);
    disc(s, 196, 46, 3, s->on ? RGB(47,194,245) : MUTED);
    if (s->on) {
      for (int x = 55; x <= 185; x += 32) {
        int y = 88 + (s->frame % 4)*5;
        line(s, x, y, x-3, y+7, RGB(47,194,245));
        line(s, x-3, y+7, x, y+14, RGB(47,194,245));
      }
    }
  }
  box(s, 0, 129, WIDTH, 31, EDGE);
  uint32_t status = s->on ? RGB(61,213,172) : INK;
  disc(s, 89, 144, 4, status);
  glyph(s, 103, 137, 'O', status);
  glyph(s, 117, 137, s->on ? 'N' : 'F', status);
  if (!s->on) glyph(s, 131, 137, 'F', status);
  buffer_write(s->display, 0, (uint8_t *)s->pixels, sizeof(s->pixels));
}

static void switched_changed(void *data, pin_t pin, uint32_t value) {
  (void)pin;
  appliance_t *s = data;
  s->on = value == HIGH;
  if (!s->on) s->frame = 0;
  render(s);
}

static void animate(void *data) {
  appliance_t *s = data;
  if (!s->on || s->kind == 0) return;
  s->frame = (s->frame+1) % 16;
  render(s);
}

void chip_init(void) {
  if (appliance_count >= 3) return;
  appliance_t *s = &appliances[appliance_count++];
  // An open NO contact must read OFF, not retain a floating HIGH.
  s->switched = pin_init("SW", INPUT_PULLDOWN);
  pin_init("GND", INPUT);
  s->kind = attr_read(attr_init("kind", 0));
  uint32_t width, height;
  s->display = framebuffer_init(&width, &height);
  if (width != WIDTH || height != HEIGHT) return;
  const pin_watch_config_t watch = {
    .edge = BOTH, .pin_change = switched_changed, .user_data = s,
  };
  pin_watch(s->switched, &watch);
  const timer_config_t timer = {.callback = animate, .user_data = s};
  timer_start(timer_init(&timer), 100000, true);
  s->on = pin_read(s->switched) == HIGH;
  render(s);
}
