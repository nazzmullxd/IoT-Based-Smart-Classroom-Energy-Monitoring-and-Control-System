export function drawHistoryChart(canvas, rows) {
  const context = canvas.getContext("2d");
  const { width, height } = canvas;
  context.clearRect(0, 0, width, height);
  context.strokeStyle = "#20334a";

  for (let index = 1; index < 5; index += 1) {
    context.beginPath();
    context.moveTo(0, (height * index) / 5);
    context.lineTo(width, (height * index) / 5);
    context.stroke();
  }

  const plot = (color, getValue, maximum) => {
    context.strokeStyle = color;
    context.lineWidth = 2;
    context.beginPath();
    rows.forEach((row, index) => {
      const x = (index * width) / Math.max(rows.length - 1, 1);
      const y = height - (getValue(row) / maximum) * height * 0.9;
      if (index === 0) {
        context.moveTo(x, y);
      } else {
        context.lineTo(x, y);
      }
    });
    context.stroke();
  };

  plot("#ffb35c", (row) => row.temperature || 0, 40);
  plot("#37d6c0", (row) => Math.min(row.illuminance || 0, 1000), 1000);
  plot("#c678dd", (row) => (row.occupancy ? 35 : 0), 40);
}
