Blockly.Blocks['1711345958911'] = {
  init: function() {
    this.jsonInit({
      "type": "1711345958911",
      "message0": "生n1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711345958911'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 30, 100, 107, 100, 56, 124, 111, 120, 170, 100, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(7)\nMOTOmove19(90, 88, 103, 100, 102, 56, 122, 113, 109, 39, 88, 99, 76, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(90, 88, 103, 100, 102, 56, 122, 113, 109, 39, 88, 179, 74, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(90, 160, 102, 100, 102, 55, 121, 93, 109, 101, 88, 179, 74, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(90, 160, 102, 100, 102, 55, 121, 93, 109, 101, 88, 169, 72, 50, 149, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(28)\nMOTOmove19(100, 75, 100, 50, 130, 138, 75, 80, 45, 33, 95, 150, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(21)\nMOTOmove19(100, 125, 100, 30, 130, 138, 75, 104, 45, 33, 95, 170, 70, 62, 125, 80, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(42)\nMOTOmove19(100, 140, 100, 20, 130, 138, 75, 110, 45, 43, 95, 180, 70, 62, 125, 80, 128, 71, 100)\nMOTOwait()\nDelayMs(900)\nMOTOsetspeed(14)\nMOTOmove19(100, 140, 100, 20, 130, 138, 75, 110, 99, 98, 101, 180, 116, 164, 66, 98, 128, 71, 100)\nMOTOwait()\nDelayMs(1000)\n";
  return code;
}

Blockly.Python['1711345958911'] = function(block) {
  let code = "robot.leju_action('生n1')\n";
  return code;
}

