Blockly.Blocks['1711337558773'] = {
  init: function() {
    this.jsonInit({
      "type": "1711337558773",
      "message0": "box-up00",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711337558773'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(64, 43, 93, 88, 148, 150, 69, 92, 120, 168, 115, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(76, 20, 158, 88, 148, 150, 69, 92, 118, 186, 44, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(79, 34, 146, 65, 130, 145, 46, 67, 121, 168, 55, 131, 64, 50, 155, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 141, 69, 124, 139, 47, 72, 137, 190, 55, 128, 67, 52, 152, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 180, 91, 114, 150, 48, 90, 137, 190, 23, 114, 84, 50, 151, 112, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 99, 107, 144, 75, 99, 120, 40, 99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711337558773'] = function(block) {
  let code = "robot.leju_action('box-up00')\n";
  return code;
}

