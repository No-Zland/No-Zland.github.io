Blockly.Blocks['1711335468007'] = {
  init: function() {
    this.jsonInit({
      "type": "1711335468007",
      "message0": "高台半成品",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711335468007'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,92,63,124,113,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,92,31,145,115,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,92,31,145,115,120,170,100,102,50,58,116,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,92,31,145,115,120,170,100,101,60,165,24,110,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,101,43,30,92,106,120,170,100,101,51,154,17,106,128,71,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(80,30,100,92,40,38,85,88,120,170,100,98,49,155,10,97,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,92,40,38,85,88,120,100,100,91,99,153,67,88,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711335468007'] = function(block) {
  let code = "robot.leju_action('高台半成品')\n";
  return code;
}

