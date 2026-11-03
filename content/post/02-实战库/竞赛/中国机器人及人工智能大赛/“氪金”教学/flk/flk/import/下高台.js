Blockly.Blocks['1711348020369'] = {
  init: function() {
    this.jsonInit({
      "type": "1711348020369",
      "message0": "下高台",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711348020369'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,25,70,70,70,70,70,25,25,25,70,70,70,70,70,0,0,0)\nMOTOsetspeed(53)\nMOTOmove19(101, 101, 101, 95, 120, 119, 85, 95, 135, 104, 99, 105, 80, 81, 115, 105, 128, 71, 100)\nMOTOwait()\nDelayMs(250)\nMOTOsetspeed(25)\nMOTOmove19(145, 155, 105, 90, 132, 138, 75, 108, 55, 45, 95, 105, 75, 85, 108, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(145, 155, 105, 78, 130, 138, 75, 110, 55, 45, 95, 110, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\n\n\n-- 4\nMOTOsetspeed(28)\nMOTOmove19(100, 75, 100, 50, 130, 138, 75, 80, 45, 33, 95, 150, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\n\n\n-- 5\nMOTOsetspeed(28)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n\n\n-- 6\nMOTOsetspeed(35)\nMOTOmove19(80, 30, 100, 108, 93, 55, 124, 100, 120, 170, 100, 92, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711348020369'] = function(block) {
  let code = "robot.leju_action('下高台')\n";
  return code;
}

