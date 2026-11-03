Blockly.Blocks['1711440056030'] = {
  init: function() {
    this.jsonInit({
      "type": "1711440056030",
      "message0": "抱块3",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711440056030'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(130)\nMOTOmove19(80, 30, 145, 100, 93, 55, 124, 100, 119, 173, 51, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 145, 92, 107, 150, 38, 100, 119, 173, 51, 101, 69, 50, 145, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(80, 30, 160, 68, 125, 150, 44, 68, 119, 173, 51, 128, 68, 50, 157, 126, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(42, 38, 173, 45, 151, 150, 46, 62, 155, 178, 35, 145, 48, 50, 155, 138, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(42, 38, 173, 59, 150, 125, 97, 67, 155, 178, 35, 118, 47, 80, 93, 127, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(32)\nMOTOmove19(42, 38, 173, 96, 113, 63, 128, 95, 155, 178, 35, 102, 86, 133, 74, 104, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711440056030'] = function(block) {
  let code = "robot.leju_action('抱块3')\n";
  return code;
}

