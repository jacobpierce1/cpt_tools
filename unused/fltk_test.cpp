// Simple Numeric Keypad for Touch Screen Applications

// Demonstrate how to use Fl_Input in a touchscreen application -erco 08/25/06
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Button.H>

class MyNumPad : public Fl_Window {
    Fl_Input *in;               // input preview
    Fl_Callback *enter_cb;      // callback when user hits 'enter'
    void *enter_data;

    // Handle numeric keypad buttons pressed
    void Button_CB2(Fl_Widget *w) {
        Fl_Button *b = (Fl_Button*)w;
        if ( strcmp(b->label(),"Del") == 0 ) {                  // handle Delete
            // Delete
            if (in->mark() != in->position()) in->cut();
            else in->cut(-1);
        }
        else if ( strcmp(b->label(), "Ent") == 0 ) {            // handle enter key
            // Do 'Enter' callback
            if ( enter_cb ) (*enter_cb)(in, enter_data);
        }
        else {                                                  // handle all other keys
            // Appends label of button
            in->replace(in->position(), in->mark(), b->label(), 1);
        }
    }
    static void Button_CB(Fl_Widget *w, void *data) {
        MyNumPad *numpad = (MyNumPad*)data;
        numpad->Button_CB2(w);
    }
public:
    MyNumPad(int X,int Y,int W=100,int H=140,const char *L=0):Fl_Window(X,Y,W,H,L) {
        const int bsize = 20;
        // Preview input
        in = new Fl_Input(X+10,Y+10,W-20,20);
        // Numeric keypad
        Fl_Button *b;
        int colstart = 10,
            col = colstart,
            row = in->y()+in->h()+10;
        b = new Fl_Button(col,row,bsize,bsize,  "7");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "8");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "9");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "Del"); b->callback(Button_CB, (void*)this); b->labelsize(10);
                                                                                             col=colstart; row+=b->h();
        b = new Fl_Button(col,row,bsize,bsize,  "4");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "5");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "6");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "-");   b->callback(Button_CB, (void*)this); col=colstart; row+=b->h();
        b = new Fl_Button(col,row,bsize,bsize,  "1");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "2");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "3");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "+");   b->callback(Button_CB, (void*)this); col=colstart; row+=b->h();
        b = new Fl_Button(col,row,bsize,bsize,  ".");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize,bsize,  "0");   b->callback(Button_CB, (void*)this); col+=b->w();
        b = new Fl_Button(col,row,bsize*2,bsize,"Ent"); b->callback(Button_CB, (void*)this); col+=b->w(); b->color(10);
        end();
        enter_cb = 0;
        enter_data = 0;
    }
    // Return current value
    const char *value() {
        return(in->value());
    }
    // Clear current value
    void clear() {
        in->value("");
    }
    // Set callback for when Enter is pressed
    void SetEnterCallback(Fl_Callback *cb, void *data) {
        enter_cb = cb;
        enter_data = data;
    }
};

class MyInput : public Fl_Input {
    MyNumPad *numpad;                   // local instance of numeric keypad widget

    // Called when user finishes entering data with numeric keypad
    void SetNumPadValue_CB2() {
        value(numpad->value());         // pass value from numpad to our input
        numpad->hide();                 // hide numpad
    }
    static void SetNumPadValue_CB(Fl_Widget*,void *data) {
        MyInput *in = (MyInput*)data;
        in->SetNumPadValue_CB2();
    }
    // Handle when user right clicks on our input widget
    int handle(int e) {
        int ret = 0;
        switch(e) {
            // Mouse click on input field? Open numpad dialog..
            case FL_PUSH:
                if ( Fl::event_button() == FL_LEFT_MOUSE ) { ret = 1; }
                break;
            case FL_RELEASE:
                if ( Fl::event_button() == FL_LEFT_MOUSE ) {
                    ret = 1;
                    if ( ! numpad ) numpad = new MyNumPad(0,0);
                    numpad->SetEnterCallback(SetNumPadValue_CB, (void*)this);
                    numpad->position(parent()->x(),parent()->y());
                    numpad->clear();
                    numpad->show();
                }
                break;
        }
        return(Fl_Input::handle(e)?1:ret);
    }
public:
    MyInput(int X,int Y,int W,int H,const char *L=0):Fl_Input(X,Y,W,H,L) {
        numpad = 0;
    }
};

int main(int argc, char **argv) {
    Fl_Window win(400,50);
    MyInput in(150,10,200,30,"Value:");
    in.value("-click here-");
    win.end();
    win.resizable(win);
    win.show();
    return(Fl::run());
}
