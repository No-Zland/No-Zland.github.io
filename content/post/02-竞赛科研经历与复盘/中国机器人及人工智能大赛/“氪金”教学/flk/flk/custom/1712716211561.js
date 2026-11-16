Blockly.Blocks['1712716211561'] = {
  init: function() {
    this.jsonInit({
      "type": "1712716211561",
      "message0": "高台box-up",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1712716211561'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,100,93,55,130,98,122,190,31,100,107,145,70,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(75,10,169,99,90,150,38,100,122,190,31,101,111,50,163,99,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(75,10,169,62,109,150,46,74,122,190,31,128,103,59,154,131,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(75,10,169,71,122,150,47,69,122,190,31,135,79,50,152,133,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,32,168,71,122,150,47,69,122,166,31,135,79,50,152,133,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1712716211561'] = function(block) {
  let code = "robot.leju_action('高台box-up')\n";
  return code;
}

