
function test(){
    this.simpleMapScreenshoter.takeScreen(format, overridedPluginOptions).then(blob => {
        alert('done')
        FileSaver.saveAs(blob, 'screen.png')
      }).catch(e => {
        console.error(e)
      })
}