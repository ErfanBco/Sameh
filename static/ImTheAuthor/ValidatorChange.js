    function ValidatorChange(){
        //window.alert('changed')
        const select = document.getElementById('Validator')
        if (select.selectedIndex === 0){
            document.getElementById('ValidatorFee').disabled = true
        }else{
            document.getElementById('ValidatorFee').disabled = false
        }
    }



