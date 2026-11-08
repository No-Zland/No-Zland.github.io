Blockly.Blocks['1711440985897'] = {
  init: function() {
    this.jsonInit({
      "type": "1711440985897",
      "message0": "box_up_x",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711440985897'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(150)\nMOTOmove19(78, 56, 100, 101, 113, 63, 128, 95, 115, 152, 101, 100, 86, 133, 74, 104, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 46, 165, 53, 154, 150, 59, 62, 127, 163, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(73, 10, 164, 53, 154, 150, 59, 62, 130, 190, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 164, 100, 93, 55, 124, 100, 138, 190, 37, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711440985897'] = function(block) {
  let code = "robot.leju_action('box_up_x')\n";
  return code;
}

