Blockly.Blocks['1711518668051'] = {
  init: function() {
    this.jsonInit({
      "type": "1711518668051",
      "message0": "xgt起身",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711518668051'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,100,93,55,124,100,97,20,190,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,100,90,59,70,99,97,20,190,100,107,136,134,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,100,133,150,36,101,97,20,190,101,63,50,165,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(86,105,105,100,133,150,36,101,115,81,95,101,63,50,165,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(90,13,190,100,133,150,36,101,113,190,10,101,63,50,165,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(90,13,145,99,111,150,39,100,113,190,60,101,89,50,164,100,128,71,96)\nMOTOwait()\nMOTOsetspeed(23)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711518668051'] = function(block) {
  let code = "robot.leju_action('xgt起身')\n";
  return code;
}

