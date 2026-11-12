Blockly.Blocks['1710424692297'] = {
  init: function() {
    this.jsonInit({
      "type": "1710424692297",
      "message0": "后退",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710424692297'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,117,51,141,107,120,170,100,98,94,119,103,110,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,95,120,73,145,97,120,170,100,96,137,114,122,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,99,116,62,138,82,120,170,100,101,79,121,76,91,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710424692297'] = function(block) {
  let code = "robot.leju_action('后退')\n";
  return code;
}

