Blockly.Blocks['1711518547621'] = {
  init: function() {
    this.jsonInit({
      "type": "1711518547621",
      "message0": "xgt推",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711518547621'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(107,169,89,100,93,55,124,100,98,20,115,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(107,168,10,100,93,55,124,100,97,20,190,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(8)\nMOTOmove19(107,169,89,99,87,90,132,100,98,20,115,99,114,113,64,98,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711518547621'] = function(block) {
  let code = "robot.leju_action('xgt推')\n";
  return code;
}

