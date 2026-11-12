Blockly.Blocks['1711351616249'] = {
  init: function() {
    this.jsonInit({
      "type": "1711351616249",
      "message0": "box-down-max-q1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711351616249'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(76,14,171,100,93,55,130,98,119,182,31,100,107,145,70,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(76,14,171,99,90,150,38,100,119,182,31,101,111,50,163,99,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(76,14,171,62,109,150,46,74,119,182,31,128,103,59,154,131,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(76,14,171,71,122,150,47,69,119,182,31,135,79,50,152,133,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(76,37,171,71,122,150,47,69,115,164,30,135,79,50,152,133,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(76,14,171,99,98,150,40,100,119,182,31,100,105,50,163,99,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711351616249'] = function(block) {
  let code = "robot.leju_action('box-down-max-q1')\n";
  return code;
}

