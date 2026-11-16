Blockly.Blocks['1711177930910'] = {
  init: function() {
    this.jsonInit({
      "type": "1711177930910",
      "message0": "sgt",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711177930910'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,93,55,124,100,120,170,41,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,99,93,54,101,99,120,170,41,100,108,144,100,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,93,55,124,100,120,170,41,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,156,10,109,98,120,170,41,100,42,190,93,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711177930910'] = function(block) {
  let code = "robot.leju_action('sgt')\n";
  return code;
}

