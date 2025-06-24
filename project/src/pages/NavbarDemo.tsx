import { Navbar1 } from "@/components/ui/navbar-1"

const NavbarDemo = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar1 />
      
      {/* Demo content to show the navbar in context */}
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Navbar Component Demo
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            This is a beautiful, animated navbar with mobile responsiveness
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-16">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-3">Desktop Features</h3>
              <ul className="text-left text-gray-600 space-y-2">
                <li>• Smooth animations with Motion</li>
                <li>• Hover effects on navigation items</li>
                <li>• Rounded full design with shadow</li>
                <li>• Gradient logo with rotation effect</li>
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-3">Mobile Features</h3>
              <ul className="text-left text-gray-600 space-y-2">
                <li>• Slide-in mobile menu</li>
                <li>• Smooth transitions</li>
                <li>• Touch-friendly interactions</li>
                <li>• Full-screen overlay design</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-16 p-8 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Try It Out</h3>
            <p className="text-gray-600 mb-4">
              Resize your browser window or use developer tools to test the responsive behavior.
              On mobile, click the menu button to see the animated slide-in menu.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <span className="px-4 py-2 bg-gray-100 rounded-full text-sm">Responsive Design</span>
              <span className="px-4 py-2 bg-gray-100 rounded-full text-sm">Motion Animations</span>
              <span className="px-4 py-2 bg-gray-100 rounded-full text-sm">Lucide Icons</span>
              <span className="px-4 py-2 bg-gray-100 rounded-full text-sm">Tailwind CSS</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NavbarDemo 