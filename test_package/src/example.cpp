//
// Created by Sileno de Oliveira Brito on 26/09/2023.
//

#include <string>
#include <vector>
#include <resip/stack/SipStack.hxx>
#include <resip/stack/SipMessage.hxx>
#include <rutil/Data.hxx>
#include <media/RTPPortManager.hxx>

int main(int argc, char **argv) {
    /// dum test
    resip::SipStack stack;
    resip::SipMessage msg;

    /// rutil test
    const char *txt = "conan";
    resip::Data d(txt);

    /// resipmedia test
    resip::RTPPortManager mPortManager;

}