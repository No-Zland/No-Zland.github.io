Blockly.Blocks['1710307416719'] = {
  init: function() {
    this.jsonInit({
      "type": "1710307416719",
      "message0": "放块pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710307416719'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,96,97,150,37,98,155,178,35,97,90,50,154,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,39,172,60,110,150,46,64,154,177,35,136,90,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,39,155,48,130,150,46,64,154,176,45,144,68,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(41,91,166,48,130,150,46,64,154,113,40,144,68,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,52,150,99,110,43,142,92,141,171,48,111,88,158,56,108,128,71,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(87,16,104,102,99,43,142,92,112,183,93,100,99,158,56,108,128,71,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710307416719'] = function(block) {
  let code = "robot.leju_action('放块pro')\n";
  return code;
}

