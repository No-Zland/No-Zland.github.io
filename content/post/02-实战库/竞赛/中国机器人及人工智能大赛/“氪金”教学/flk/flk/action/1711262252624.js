Blockly.Blocks['1711262252624'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262252624",
      "message0": "box_Rturn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262252624'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(64,10,179,100,93,55,124,100,137,190,23,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,179,91,132,34,190,91,137,190,23,106,167,138,137,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,179,100,93,55,124,100,137,190,23,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711262252624'] = function(block) {
  let code = "robot.leju_action('box_Rturn')\n";
  return code;
}

